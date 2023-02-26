#!/usr/bin/env python3

"""
 SPDX-License-Identifier: MIT

 Copyright (C) 2022-2023 Advanced Micro Devices, Inc.

 Shows multiple PROGBITS sections
"""

import sys
import ctypes
import random

import pylibelf.elf
import pylibelf.libelf

import testhelper

def populate_random_numbers(size):
    words = (ctypes.c_uint * size)()
    for index in range(size):
#        words[index] = index
        words[index] = int(random.random() * 0xffffffff)
    return words

def populate_text_and_data_sections(strtab, melf):
    # Populate text segment
    scn = melf.elf_newscn()
    scn_data = scn.elf_newdata()

    words = populate_random_numbers(64)
    scn_data.contents.d_align = 8
    scn_data.contents.d_off = 0
    scn_data.contents.d_buf = ctypes.cast(words, ctypes.c_void_p)
    scn_data.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_WORD
    scn_data.contents.d_size = ctypes.sizeof(words)
    scn_data.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".ctrltext")
    shdr.contents.sh_type = pylibelf.elf.SHT_PROGBITS
    shdr.contents.sh_flags = pylibelf.elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    # Populate data segment
    scn = melf.elf_newscn()
    scn_data = scn.elf_newdata()

    words = populate_random_numbers(32)
    scn_data.contents.d_align = 16
    scn_data.contents.d_off = 0
    scn_data.contents.d_buf = ctypes.cast(words, ctypes.c_void_p)
    scn_data.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_WORD
    scn_data.contents.d_size = ctypes.sizeof(words)
    scn_data.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".ctrldata")
    shdr.contents.sh_type = pylibelf.elf.SHT_PROGBITS
    shdr.contents.sh_flags = pylibelf.elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0


def write_ELF(filename):
    strtab = testhelper.ElfStringTable()
    melf = pylibelf.libelf.ElfDescriptor.fromfile(filename, pylibelf.libelf.Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[pylibelf.elf.EI_DATA] = pylibelf.elf.ELFDATA2LSB
    ehdr.contents.e_ident[pylibelf.elf.EI_VERSION] = pylibelf.elf.EV_CURRENT
    # Our own ABI version
    ehdr.contents.e_ident[pylibelf.elf.EI_OSABI] = 0x40
    ehdr.contents.e_ident[pylibelf.elf.EI_ABIVERSION] = 0x1
    # Repurpose obsolete EM_M32 for our machine type
    ehdr.contents.e_machine = pylibelf.elf.EM_M32
    ehdr.contents.e_type = pylibelf.elf.ET_EXEC
    ehdr.contents.e_flags = 0x0;

    strtab.add("")

    phdr = melf.elf32_newphdr(2)

    populate_text_and_data_sections(strtab, melf)

    populate_text_and_data_sections(strtab, melf)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()
    data.contents.d_align = 1
    data.contents.d_off = 0
    data.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".shstrtab")
    shdr.contents.sh_type = pylibelf.elf.SHT_STRTAB
    shdr.contents.sh_flags = pylibelf.elf.SHF_STRINGS | pylibelf.elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    # Now that all sections have been named, create the native symbol table buffer
    symsdata = strtab.packsyms()
    data.contents.d_size = ctypes.sizeof(symsdata)
    data.contents.d_buf = ctypes.cast(symsdata, ctypes.c_void_p)
    ehdr.contents.e_shstrndx = scn.elf_ndxscn()

    melf.elf_update(pylibelf.libelf.Elf_Cmd.ELF_C_NULL)

    phdr[0].p_type = pylibelf.elf.PT_PHDR
    phdr[0].p_offset = ehdr.contents.e_phoff
    phdr[0].p_vaddr = ehdr.contents.e_phoff
    phdr[0].p_paddr = ehdr.contents.e_phoff
    phdr[0].p_filesz = pylibelf.libelf.elf32_fsize(pylibelf.libelf.Elf_Type.ELF_T_PHDR, 1, pylibelf.elf.EV_CURRENT)
    phdr[0].p_memsz = pylibelf.libelf.elf32_fsize(pylibelf.libelf.Elf_Type.ELF_T_PHDR, 1, pylibelf.elf.EV_CURRENT)
    phdr[0].p_flags = pylibelf.elf.PF_R
    phdr[0].p_align = 0x8

    phdr[1].p_type = pylibelf.elf.PT_LOAD
    phdr[1].p_offset = 0
    phdr[1].p_vaddr = 0
    phdr[1].p_paddr = 0
    # Everything before section headers is normally application code, hence load them
    phdr[1].p_filesz = ehdr.contents.e_shoff
    phdr[1].p_memsz = ehdr.contents.e_shoff
    phdr[1].p_flags = pylibelf.elf.PF_R | pylibelf.elf.PF_X
    phdr[1].p_align = 0x10

    melf.elf_flagphdr(pylibelf.libelf.Elf_Cmd.ELF_C_SET , pylibelf.libelf.ELF_F_DIRTY)

    curr = melf.elf_nextscn(None)
    while (curr is not None) :
        curr_shdr = curr.elf32_getshdr()
        name = curr_shdr.contents.sh_name
        offset = curr_shdr.contents.sh_offset
        size = curr_shdr.contents.sh_size
        print(f"[{strtab.get(name)} O {offset}, S {size}]")
        curr = melf.elf_nextscn(curr)

    melf.elf_update(pylibelf.libelf.Elf_Cmd.ELF_C_WRITE)

if __name__ == "__main__":
    argtab = testhelper.parse_command_line(sys.argv)

    if (argtab.filename != None and argtab.filename[0] != None):
        print(f"Writing ELF file {argtab.filename[0]}")
        write_ELF(argtab.filename[0])
        testhelper.validate_ELF(argtab.filename[0], argtab.reference)
    elif (argtab.decompile != None and argtab.decompile[0] != None):
        print(f"Reading ELF file {argtab.decompile[0]}")
        testhelper.read_ELF(argtab.decompile[0])
