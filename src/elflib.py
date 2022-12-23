"""
 SPDX-License-Identifier: GPL-3.0-or-later

 Copyright (C) 2022 Advanced Micro Devices, Inc.

 ctypes based Python binding for libelf
"""

import os
import sys
import errno
import ctypes
import warnings
import enum

from elf import *

libelf = ctypes.CDLL("libelf.so", mode=ctypes.RTLD_GLOBAL)

"""A ctypes-compatible IntEnum superclass."""
class CtypesEnum(enum.IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)

"""For definition of the enum literals see libelf.h."""
class Elf_Type(CtypesEnum):
    ELF_T_BYTE = 0
    ELF_T_ADDR = 1
    ELF_T_DYN =  2
    ELF_T_EHDR = 3
    ELF_T_HALF = 4
    ELF_T_OFF =  5
    ELF_T_PHDR = 6
    ELF_T_RELA = 7
    ELF_T_REL =  8
    ELF_T_SHDR = 9
    ELF_T_SWORD = 10
    ELF_T_SYM =   11
    ELF_T_WORD =  12
    ELF_T_XWORD = 13
    ELF_T_SXWORD = 14
    ELF_T_VDEF = 15
    ELF_T_VDAUX = 16
    ELF_T_VNEED = 17
    ELF_T_VNAUX = 18
    ELF_T_NHDR = 19
    ELF_T_SYMINFO = 20
    ELF_T_MOVE = 21
    ELF_T_LIB = 22
    ELF_T_GNUHASH = 23
    ELF_T_AUXV = 24
    ELF_T_CHDR = 25
    ELF_T_NHDR8 = 26
    ELF_T_NUM = 27

class Elf_Cmd(CtypesEnum):
    ELF_C_NULL = 0
    ELF_C_READ = 1
    ELF_C_RDWR = 2
    ELF_C_WRITE = 3
    ELF_C_CLR = 4
    ELF_C_SET = 5
    ELF_C_FDDONE = 6
    ELF_C_FDREAD = 7
    ELF_C_READ_MMAP = 8
    ELF_C_RDWR_MMAP = 9
    ELF_C_WRITE_MMAP = 10
    ELF_C_READ_MMAP_PRIVATE = 11
    ELF_C_EMPTY = 12
    ELF_C_NUM = 13


ELF_F_DIRTY = 0x1
ELF_F_LAYOUT = 0x4
ELF_F_PERMISSIVE = 0x8

class Elf_Kind(CtypesEnum):
    ELF_K_NONE = 0
    ELF_K_AR = 1
    ELF_K_COFF = 2
    ELF_K_ELF = 3
    ELF_K_NUM = 4


class ElfError(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.errno = libelf.elf_errno()
        self.errmsg = libelf.elf_errmsg(errno)

    def __str__(self):
        return self.errmsg

def _valueOrError(res):
    """
    Validate returned pointer
    """
    if (res == None):
        raise ElfError()
    return res

class Elf_Data(ctypes.Structure):
    _fields_ = [
        ("d_buf", ctypes.c_void_p),
        ("d_type", ctypes.c_int),
        ("d_version", ctypes.c_uint),
        ("d_size", ctypes.c_size_t),
        ("d_off", ctypes.c_longlong),
        ("d_align", ctypes.c_size_t) ]


class Elf_ScnDescriptor:
    def __init__(self, scn):
        self.scn = scn

    def elf32_getshdr(self):
        return libelf.elf32_getshdr(self.scn)

    def elf_newdata(self):
        return libelf.elf_newdata(self.scn)

class ElfDescriptor:
    def __init__(self, elf, filehandle = None):
        self.filehandle = filehandle
        self.elf = elf

    def __del__(self):
        libelf.elf_end(self.elf)
        if (self.filehandle != None):
            self.filehandle.close()

    @classmethod
    def fromfile(cls, filename, cmd):
        filehandle = open(filename, "wb+")
        elf = libelf.elf_begin(filehandle.fileno(), cmd, None)
        return cls(elf, filehandle)

    @classmethod
    def frommemory(cls, image, size):
        elf = libelf.elf_memory(image, size)
        return cls(elf)

    def elf_kind(self):
        return libelf.elf_kind(self.elf);

    def elf32_newehdr(self):
        return libelf.elf32_newehdr(self.elf);

    def elf32_newphdr(self, count):
        return libelf.elf32_newphdr(self.elf, count)

    def elf_flagphdr(self, cmd, flags):
        return libelf.elf_flagphdr(self.elf, cmd, flags)

    def elf_update(self, cmd):
        return libelf.elf_update(self.elf, cmd)

    def elf_newscn(self):
        scn = libelf.elf_newscn(self.elf)
        return Elf_ScnDescriptor(scn)

def elf32_fsize(typ, count, version):
    return libelf.elf32_fsize(typ, count, version)

def setup():
    libelf.elf_begin.restype = ctypes.c_void_p
    libelf.elf_begin.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]

    libelf.elf_end.restype = ctypes.c_int
    libelf.elf_end.argtypes = [ctypes.c_void_p]

    libelf.elf_version.restype = ctypes.c_uint
    libelf.elf_version.argtypes = [ctypes.c_uint]

    libelf.elf_kind.restype = ctypes.c_uint
    libelf.elf_kind.argtypes = [ctypes.c_void_p]

    libelf.elf32_newehdr.restype = ctypes.POINTER(Elf32_Ehdr)
    libelf.elf32_newehdr.argtypes = [ctypes.c_void_p]

    libelf.elf32_newphdr.restype = ctypes.POINTER(Elf32_Phdr)
    libelf.elf32_newphdr.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

    libelf.elf_flagphdr.restype = ctypes.c_uint
    libelf.elf_flagphdr.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint]

    libelf.elf_update.restype = ctypes.c_int
    libelf.elf_update.argtypes = [ctypes.c_void_p, ctypes.c_int]

    libelf.elf32_fsize.restype = ctypes.c_size_t
    libelf.elf32_fsize.argtypes = [ctypes.c_int, ctypes.c_size_t, ctypes.c_uint]

    libelf.elf_newscn.restype = ctypes.c_void_p
    libelf.elf_newscn.argtypes = [ctypes.c_void_p]

    libelf.elf32_getshdr.restype = ctypes.POINTER(Elf32_Shdr)
    libelf.elf32_getshdr.argtypes = [ctypes.c_void_p]

    libelf.elf_newdata.restype = ctypes.POINTER(Elf_Data)
    libelf.elf_newdata.argtypes = [ctypes.c_void_p]

    res = libelf.elf_version(1)

if __name__ == "__main__":
    setup()
    melf = ElfDescriptor.fromfile("hello.elf", Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[EI_DATA] = ELFDATA2MSB
    ehdr.contents.e_machine = EM_PPC
    ehdr.contents.e_type = ET_EXEC

    phdr = melf.elf32_newphdr(1)

    scn = melf.elf_newscn()

    data = scn.elf_newdata()

    hash_words = (c_int * 3)(0x01234567, 0x89abcdef, 0xdeadc0de)
    data.d_align = 4;
    data.d_off = 0LL ;
    data.d_buf = hash_words ;
    data.d_type = ELF_T_WORD ;
    data.d_size = ctypes.sizeof(hash_words)
    data.d_type = ELF_T_BYTE ;
    data.d_version = EV_CURRENT ;

    shdr = scn.elf32_getshdr()
    shdr.contents.sh_name = 6
    shdr.contents.sh_type = SHT_STRTAB
    shdr.contents.sh_flags = SHF_STRINGS | SHF_ALLOC
    shdr.contents.sh_entsize = 0
    melf.elf_update(Elf_Cmd.ELF_C_NULL)

    phdr.contents.p_type = PT_PHDR
    phdr.contents.p_offset = ehdr.contents.e_phoff
    phdr.contents.p_filesz = elf32_fsize(Elf_Type.ELF_T_PHDR, 1, EV_CURRENT)
    melf.elf_flagphdr(Elf_Cmd.ELF_C_SET , ELF_F_DIRTY)
    melf.elf_update(Elf_Cmd.ELF_C_WRITE)

    del melf
