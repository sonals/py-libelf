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

    def elf_update(self, cmd):
        return libelf.elf_update(self.elf, cmd)


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
    libelf.elf_update.restype = ctypes.c_int
    libelf.elf_update.argtypes = [ctypes.c_void_p, ctypes.c_int]

    res = libelf.elf_version(1)

if __name__ == "__main__":
    setup()
    melf = ElfDescriptor.fromfile("hello.elf", Elf_Cmd.ELF_C_WRITE)
    ehdr = melf.elf32_newehdr()

    ehdr.contents.e_ident[EI_DATA] = ELFDATA2MSB
    ehdr.contents.e_machine = EM_PPC
    ehdr.contents.e_type = ET_EXEC

    melf.elf_update(Elf_Cmd.ELF_C_WRITE)

    del melf
