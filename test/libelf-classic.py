#!/usr/bin/env python3

"""
 SPDX-License-Identifier: Apache-2.0

 Copyright (C) 2022 Advanced Micro Devices, Inc.

 ctypes based Python binding for libelf
"""

import sys
import argparse
from elf import *
from libelf import *

def parseCommandLine(args):
    msg = "Write out a sample ELF file"
    parser = argparse.ArgumentParser(description = msg, exit_on_error = True)
    parser.add_argument(dest ='filename', nargs = 1)
    # strip out the argv[0]
    return parser.parse_args(args[1:])

def writeELF(filename):
    melf = ElfDescriptor.fromfile(filename, Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[EI_DATA] = ELFDATA2MSB
    ehdr.contents.e_machine = EM_PPC
    ehdr.contents.e_type = ET_EXEC

    phdr = melf.elf32_newphdr(1)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()

    hash_words = (ctypes.c_uint * 3)(0x01234567, 0x89abcdef, 0xdeadc0de)
    data.contents.d_align = 4
    data.contents.d_off = 0
    data.contents.d_buf = ctypes.cast(hash_words, ctypes.c_void_p)
    data.contents.d_type = Elf_Type.ELF_T_WORD
    data.contents.d_size = ctypes.sizeof(hash_words)
    data.contents.d_type = Elf_Type.ELF_T_BYTE
    data.contents.d_version = EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = 1
    shdr.contents.sh_type = SHT_HASH
    shdr.contents.sh_flags = SHF_ALLOC
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
    data2.contents.d_type = Elf_Type.ELF_T_BYTE
    data2.contents.d_version = EV_CURRENT

    shdr2 = scn2.elf32_getshdr()
    shdr2.contents.sh_name = 6
    shdr2.contents.sh_type = SHT_STRTAB
    shdr2.contents.sh_flags = SHF_STRINGS | SHF_ALLOC
    shdr2.contents.sh_entsize = 0


    ehdr.contents.e_shstrndx = scn2.elf_ndxscn()

    melf.elf_update(Elf_Cmd.ELF_C_NULL)

    phdr.contents.p_type = PT_PHDR
    phdr.contents.p_offset = ehdr.contents.e_phoff
    phdr.contents.p_filesz = elf32_fsize(Elf_Type.ELF_T_PHDR, 1, EV_CURRENT)
    melf.elf_flagphdr(Elf_Cmd.ELF_C_SET , ELF_F_DIRTY)
    melf.elf_update(Elf_Cmd.ELF_C_WRITE)

    del melf

if __name__ == "__main__":
    argtab = parseCommandLine(sys.argv)
    print(f"Writing ELF file {argtab.filename[0]}")
    writeELF(argtab.filename[0])
