#!/usr/bin/env python3

"""
 SPDX-License-Identifier: Apache-2.0

 Copyright (C) 2022 Advanced Micro Devices, Inc.

 Shows multiple PROGBITS sections
"""

import sys
import argparse
import ctypes
import random
import subprocess
import hashlib

import elf
import libelf


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

def validateELF(elfname, goldname):
    result = subprocess.run(["readelf", "-a", elfname], capture_output = True)
    sig = hashlib.md5(result.stdout).hexdigest()
    goldsig = None

    if (goldname is None):
        return

    with open(goldname, "rb") as goldhandle:
        gold = goldhandle.read()
        goldsig = hashlib.md5(gold).hexdigest()
    assert(sig == goldsig), "ELF headers mismatch for " + elfname

def parse_command_line(args):
    msg = "Write out a sample ELF file"
    parser = argparse.ArgumentParser(description = msg, exit_on_error = True)
    parser.add_argument("-o", "--output", dest ='filename', nargs = 1)
    parser.add_argument("-r", "--reference", dest ='reference', nargs = '?')
    # strip out the argv[0]
    return parser.parse_args(args[1:])

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
    scn_data.contents.d_align = 4
    scn_data.contents.d_off = 0
    scn_data.contents.d_buf = ctypes.cast(words, ctypes.c_void_p)
    scn_data.contents.d_type = libelf.Elf_Type.ELF_T_WORD
    scn_data.contents.d_size = ctypes.sizeof(words)
    scn_data.contents.d_version = elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".ctrltext")
    shdr.contents.sh_type = elf.SHT_PROGBITS
    shdr.contents.sh_flags = elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    # Populate text segment
    scn = melf.elf_newscn()
    scn_data = scn.elf_newdata()

    words = populate_random_numbers(32)
    scn_data.contents.d_align = 4
    scn_data.contents.d_off = 0
    scn_data.contents.d_buf = ctypes.cast(words, ctypes.c_void_p)
    scn_data.contents.d_type = libelf.Elf_Type.ELF_T_WORD
    scn_data.contents.d_size = ctypes.sizeof(words)
    scn_data.contents.d_version = elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".ctrldata")
    shdr.contents.sh_type = elf.SHT_PROGBITS
    shdr.contents.sh_flags = elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0


def write_ELF(filename):
    strtab = ElfStringTable()
    melf = libelf.ElfDescriptor.fromfile(filename, libelf.Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[elf.EI_DATA] = elf.ELFDATA2MSB
    ehdr.contents.e_machine = elf.EM_AVR32
    ehdr.contents.e_type = elf.ET_EXEC

    strtab.add("")

    phdr = melf.elf32_newphdr(1)

    populate_text_and_data_sections(strtab, melf)

    populate_text_and_data_sections(strtab, melf)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()
    data.contents.d_align = 1
    data.contents.d_off = 0
    data.contents.d_type = libelf.Elf_Type.ELF_T_BYTE
    data.contents.d_version = elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".shstrtab")
    shdr.contents.sh_type = elf.SHT_STRTAB
    shdr.contents.sh_flags = elf.SHF_STRINGS | elf.SHF_ALLOC
    shdr.contents.sh_entsize = 0

    # Now that all sections have been named, create the native symbol table buffer
    symsdata = strtab.packsyms()
    data.contents.d_size = ctypes.sizeof(symsdata)
    data.contents.d_buf = ctypes.cast(symsdata, ctypes.c_void_p)
    ehdr.contents.e_shstrndx = scn.elf_ndxscn()

    melf.elf_update(libelf.Elf_Cmd.ELF_C_NULL)

    phdr.contents.p_type = elf.PT_PHDR
    phdr.contents.p_offset = ehdr.contents.e_phoff
    phdr.contents.p_filesz = libelf.elf32_fsize(libelf.Elf_Type.ELF_T_PHDR, 1, elf.EV_CURRENT)
    melf.elf_flagphdr(libelf.Elf_Cmd.ELF_C_SET , libelf.ELF_F_DIRTY)
    melf.elf_update(libelf.Elf_Cmd.ELF_C_WRITE)

if __name__ == "__main__":
    argtab = parse_command_line(sys.argv)
    print(f"Writing ELF file {argtab.filename[0]}")
    write_ELF(argtab.filename[0])

    validateELF(argtab.filename[0], argtab.reference)
