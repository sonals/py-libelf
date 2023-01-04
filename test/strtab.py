#!/usr/bin/env python3

"""
 SPDX-License-Identifier: Apache-2.0

 Copyright (C) 2022-2023 Advanced Micro Devices, Inc.

 Dynamically populate the strtab based on section names
"""

import sys
import ctypes

import elf
import libelf

import testhelper

class ElfStringTable:
    def __init__(self):
        self.size = 0
        self.syms = []
    def add(self, item):
        pos = self.size
        self.syms.append(item)
        self.size += (len(item) + 1)
        return pos

    def packsyms(self):
        data = ctypes.create_string_buffer(self.size)
        index = 0
        for item in self.syms:
            arr = bytes(item, "utf-8")
            for element in arr:
                data[index] = element
                index += 1
            data[index] = b'\0'
            index += 1
        return data

def write_ELF(filename):
    strtab = ElfStringTable()
    melf = libelf.ElfDescriptor.fromfile(filename, libelf.Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[elf.EI_DATA] = elf.ELFDATA2MSB
    ehdr.contents.e_machine = elf.EM_PPC
    ehdr.contents.e_type = elf.ET_EXEC

    strtab.add("")

    phdr = melf.elf32_newphdr(1)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()

    hash_words = (ctypes.c_uint * 3)(0x01234567, 0x89abcdef, 0xdeadc0de)
    data.contents.d_align = 4
    data.contents.d_off = 0
    data.contents.d_buf = ctypes.cast(hash_words, ctypes.c_void_p)
    data.contents.d_type = libelf.Elf_Type.ELF_T_WORD
    data.contents.d_size = ctypes.sizeof(hash_words)
    data.contents.d_version = elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".foo")
    shdr.contents.sh_type = elf.SHT_HASH
    shdr.contents.sh_flags = elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    scn2 = melf.elf_newscn()
    data2 = scn2.elf_newdata()
    data2.contents.d_align = 1
    data2.contents.d_off = 0
    data2.contents.d_type = libelf.Elf_Type.ELF_T_BYTE
    data2.contents.d_version = elf.EV_CURRENT

    shdr2 = scn2.elf32_getshdr()
    shdr2.contents.sh_name = strtab.add(".shstrtab")
    shdr2.contents.sh_type = elf.SHT_STRTAB
    shdr2.contents.sh_flags = elf.SHF_STRINGS | elf.SHF_ALLOC
    shdr2.contents.sh_entsize = 0

    symsdata = strtab.packsyms()
    data2.contents.d_size = ctypes.sizeof(symsdata)
    data2.contents.d_buf = ctypes.cast(symsdata, ctypes.c_void_p)

    ehdr.contents.e_shstrndx = scn2.elf_ndxscn()

    melf.elf_update(libelf.Elf_Cmd.ELF_C_NULL)

    phdr.contents.p_type = elf.PT_PHDR
    phdr.contents.p_offset = ehdr.contents.e_phoff
    phdr.contents.p_filesz = libelf.elf32_fsize(libelf.Elf_Type.ELF_T_PHDR, 1, elf.EV_CURRENT)
    melf.elf_flagphdr(libelf.Elf_Cmd.ELF_C_SET , libelf.ELF_F_DIRTY)
    melf.elf_update(libelf.Elf_Cmd.ELF_C_WRITE)

if __name__ == "__main__":
    argtab = testhelper.parse_command_line(sys.argv)
    print(f"Writing ELF file {argtab.filename[0]}")
    write_ELF(argtab.filename[0])

    testhelper.validate_ELF(argtab.filename[0], argtab.reference)
