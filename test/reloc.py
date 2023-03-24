#!/usr/bin/env python3

"""
 SPDX-License-Identifier: MIT

 Copyright (C) 2023 Advanced Micro Devices, Inc.

 Dynamically populate the strtab based on section names
"""

import sys
import ctypes

import pylibelf.elf
import pylibelf.libelf

import testhelper

def write_Rela(melf, strtab, symtab, textindex, dynsymindex):
    rtab = testhelper.ElfRelaTable()
    scn3 = melf.elf_newscn()
    data3 = scn3.elf_newdata()
    data3.contents.d_align = 8
    data3.contents.d_off = 0
    data3.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data3.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr3 = scn3.elf32_getshdr()
    shdr3.contents.sh_name = strtab.add(".rela.dyn")
    shdr3.contents.sh_type = pylibelf.elf.SHT_RELA
    shdr3.contents.sh_flags = pylibelf.elf.SHF_ALLOC
    shdr3.contents.sh_entsize = ctypes.sizeof(pylibelf.elf.Elf32_Rela)
    shdr3.contents.sh_link = dynsymindex
    shdr3.contents.sh_info = textindex

    pos = 0
    # Some random location in the text segment
    addr = 8
    index = 0

    for item in symtab:
        rtab.add(pylibelf.elf.Elf32_Rela(addr, pylibelf.elf.ELF32_R_INFO(index, pylibelf.elf.R_M32R_32_RELA), 0))
        # Another random location in text segment
        addr += 16
        index += 1

    rdata = rtab.packsyms()
    data3.contents.d_size = ctypes.sizeof(rdata)
    data3.contents.d_buf = ctypes.cast(rdata, ctypes.c_void_p)


def write_Symtab(melf, strtab, textindex):
    dstrtab = testhelper.ElfStringTable()
    symtab = testhelper.ElfSymbolTable()
    scn3 = melf.elf_newscn()
    data3 = scn3.elf_newdata()
    data3.contents.d_align = 1
    data3.contents.d_off = 0
    data3.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data3.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr3 = scn3.elf32_getshdr()
    shdr3.contents.sh_name = strtab.add(".dynstr")
    shdr3.contents.sh_type = pylibelf.elf.SHT_STRTAB
    shdr3.contents.sh_flags = pylibelf.elf.SHF_STRINGS | pylibelf.elf.SHF_ALLOC
    shdr3.contents.sh_entsize = 0

    defaultlocal = dstrtab.add("")
    symtab.add(pylibelf.elf.Elf32_Sym(defaultlocal, 0, 0, 0, 0, pylibelf.elf.SHN_UNDEF))

    syminfo = pylibelf.elf.ELF32_ST_INFO(pylibelf.elf.STB_GLOBAL, pylibelf.elf.STT_FUNC)
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("myfunc"), 0, 0, syminfo, 0, textindex))
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("hisfunc"), 0, 0, syminfo, 0, textindex))
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("herfunc"), 0, 0, syminfo, 0, textindex))

    syminfo = pylibelf.elf.ELF32_ST_INFO(pylibelf.elf.STB_GLOBAL, pylibelf.elf.STT_OBJECT)
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("myvar"), 0, 0, syminfo, 0, textindex))
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("hisvar"), 0, 0, syminfo, 0, textindex))
    symtab.add(pylibelf.elf.Elf32_Sym(dstrtab.add("hervar"), 0, 0, syminfo, 0, textindex))

    dsymsdata = dstrtab.packsyms()
    data3.contents.d_size = ctypes.sizeof(dsymsdata)
    data3.contents.d_buf = ctypes.cast(dsymsdata, ctypes.c_void_p)


    scn4 = melf.elf_newscn()
    data4 = scn4.elf_newdata()
    data4.contents.d_align = 8
    data4.contents.d_off = 0
    data4.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data4.contents.d_version = pylibelf.elf.EV_CURRENT

    symsdata = symtab.packsyms()
    data4.contents.d_size = ctypes.sizeof(symsdata)
    data4.contents.d_buf = ctypes.cast(symsdata, ctypes.c_void_p)

    shdr4 = scn4.elf32_getshdr()
    shdr4.contents.sh_name = strtab.add(".dynsym")
    shdr4.contents.sh_type = pylibelf.elf.SHT_DYNSYM
    shdr4.contents.sh_flags = pylibelf.elf.SHF_ALLOC
    shdr4.contents.sh_entsize = ctypes.sizeof(pylibelf.elf.Elf32_Sym)
    shdr4.contents.sh_link = scn3.elf_ndxscn()
    shdr4.contents.sh_info = defaultlocal + 1

    write_Rela(melf, strtab, symtab, textindex, scn4.elf_ndxscn())

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
    ehdr.contents.e_flags = 0x0

    strtab.add("")

    phdr = melf.elf32_newphdr(2)

    scn = melf.elf_newscn()
    data = scn.elf_newdata()

    text_words = (ctypes.c_uint * 64)(0x01234567, 0x89abcdef, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0x01234567, 0x89abcdef, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0x01234567, 0x89abcdef, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0x01234567, 0x89abcdef, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de,
                                      0xdeadc0de, 0xdeadc0de, 0xdeadc0de, 0xdeadc0de)
    data.contents.d_align = 4
    data.contents.d_off = 0
    data.contents.d_buf = ctypes.cast(text_words, ctypes.c_void_p)
    data.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_WORD
    data.contents.d_size = ctypes.sizeof(text_words)
    data.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = strtab.add(".text")
    shdr.contents.sh_type = pylibelf.elf.SHT_PROGBITS
    shdr.contents.sh_flags = pylibelf.elf.SHF_ALLOC | pylibelf.elf.SHF_EXECINSTR
    shdr.contents.sh_entsize = 0

    scn2 = melf.elf_newscn()
    data2 = scn2.elf_newdata()
    data2.contents.d_align = 1
    data2.contents.d_off = 0
    data2.contents.d_type = pylibelf.libelf.Elf_Type.ELF_T_BYTE
    data2.contents.d_version = pylibelf.elf.EV_CURRENT

    shdr2 = scn2.elf32_getshdr()
    shdr2.contents.sh_name = strtab.add(".shstrtab")
    shdr2.contents.sh_type = pylibelf.elf.SHT_STRTAB
    shdr2.contents.sh_flags = pylibelf.elf.SHF_STRINGS | pylibelf.elf.SHF_ALLOC
    shdr2.contents.sh_entsize = 0

    write_Symtab(melf, strtab, scn.elf_ndxscn())
    symsdata = strtab.packsyms()
    data2.contents.d_size = ctypes.sizeof(symsdata)
    data2.contents.d_buf = ctypes.cast(symsdata, ctypes.c_void_p)

    ehdr.contents.e_shstrndx = scn2.elf_ndxscn()

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
