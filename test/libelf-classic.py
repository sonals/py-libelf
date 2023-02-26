#!/usr/bin/env python3

"""
 SPDX-License-Identifier: MIT

 Copyright (C) 2022-2023 Advanced Micro Devices, Inc.

 Port of classic "Creating new ELF objects" from "libelf by Example"
"""

import sys
import ctypes

import pylibelf.elf
import pylibelf.libelf

import testhelper

def write_ELF(filename):
    melf = pylibelf.libelf.ElfDescriptor.fromfile(filename, pylibelf.libelf.Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[pylibelf.elf.EI_DATA] = pylibelf.elf.ELFDATA2MSB
    ehdr.contents.e_machine = pylibelf.elf.EM_PPC
    ehdr.contents.e_type = pylibelf.elf.ET_EXEC

    phdr = melf.elf32_newphdr(1)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()

    hash_words = (ctypes.c_uint * 3)(0x01234567, 0x89abcdef, 0xdeadc0de)
    data.contents.d_align = 4
    data.contents.d_off = 0
    data.contents.d_buf = ctypes.cast(hash_words, ctypes.c_void_p)
    data.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_WORD
    data.contents.d_size = ctypes.sizeof(hash_words)
    data.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = 1
    shdr.contents.sh_type = pylibelf.elf.SHT_HASH
    shdr.contents.sh_flags = pylibelf.elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    scn2 = melf.elf_newscn()
    data2 = scn2.elf_newdata()

    string_table = (ctypes.c_char * 16)(b'\0' , b'.' ,b'f' , b'o' , b'o' , b'\0' ,
                                        b'.' , b's' , b'h' , b's' , b't' , b'r' ,
                                        b't' , b'a' , b'b' , b'\0')
    data2.contents.d_align = 1
    data2.contents.d_buf = ctypes.cast(string_table, ctypes.c_void_p)
    data2.contents.d_off = 0
    data2.contents.d_size = ctypes.sizeof(string_table)
    data2.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data2.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr2 = scn2.elf32_getshdr()
    shdr2.contents.sh_name = 6
    shdr2.contents.sh_type = pylibelf.elf.SHT_STRTAB
    shdr2.contents.sh_flags = pylibelf.elf.SHF_STRINGS | pylibelf.elf.SHF_ALLOC
    shdr2.contents.sh_entsize = 0


    ehdr.contents.e_shstrndx = scn2.elf_ndxscn()

    melf.elf_update(pylibelf.libelf.Elf_Cmd.ELF_C_NULL)

    phdr.contents.p_type = pylibelf.elf.PT_PHDR
    phdr.contents.p_offset = ehdr.contents.e_phoff
    phdr.contents.p_filesz = pylibelf.libelf.elf32_fsize(pylibelf.libelf.Elf_Type.ELF_T_PHDR, 1, pylibelf.elf.EV_CURRENT)
    melf.elf_flagphdr(pylibelf.libelf.Elf_Cmd.ELF_C_SET , pylibelf.libelf.ELF_F_DIRTY)
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
