"""
 SPDX-License-Identifier: LGPL-3.0-or-later OR GPL-2.0-or-later

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

_libelf = ctypes.CDLL("libelf.so", mode=ctypes.RTLD_GLOBAL)

"""A ctypes-compatible IntEnum superclass."""
class CtypesEnum(enum.IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)

"""For definition of the enumeration literals see libelf.h."""
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
    ELF_K_AR   = 1
    ELF_K_COFF = 2
    ELF_K_ELF  = 3
    ELF_K_NUM  = 4


class ElfError(Exception):
    def __init__(self, *args):
        super().__init__(args)
        self.errno = _libelf.elf_errno()
        self.errmsg = _libelf.elf_errmsg(errno)

    def __str__(self):
        return self.errmsg

def _NotNullOrError(res):
    """
    Validate returned pointer
    """
    if (res == None):
        raise ElfError()
    return res

def _TrueOrError(res):
    """
    Validate return status
    """
    if (res == 0):
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
        return _NotNullOrError(_libelf.elf32_getshdr(self.scn))

    def elf_newdata(self):
        return _NotNullOrError(_libelf.elf_newdata(self.scn))

    def elf_ndxscn(self):
        return _libelf.elf_ndxscn(self.scn)

class ElfDescriptor:
    def _cleanup(self):
        if (self.elf != None):
            _libelf.elf_end(self.elf)
        if (self.filehandle != None):
            self.filehandle.close()

    def __init__(self, elf, filehandle = None):
        self.filehandle = filehandle
        self.elf = elf

    def __del__(self):
        self._cleanup()

    @classmethod
    def fromfile(cls, filename, cmd):
        filehandle = open(filename, "wb+")
        elf = _libelf.elf_begin(filehandle.fileno(), cmd, None)
        return cls(_NotNullOrError(elf), filehandle)

    @classmethod
    def frommemory(cls, image, size):
        elf = _libelf.elf_memory(image, size)
        return cls(_NotNullOrError(elf))

    def elf_kind(self):
        return _libelf.elf_kind(self.elf);

    def elf32_newehdr(self):
        return _NotNullOrError(_libelf.elf32_newehdr(self.elf))

    def elf32_newphdr(self, count):
        return _NotNullOrError(_libelf.elf32_newphdr(self.elf, count))

    def elf_flagphdr(self, cmd, flags):
        return _NotNullOrError(_libelf.elf_flagphdr(self.elf, cmd, flags))

    def elf_update(self, cmd):
        return _NotNullOrError(_libelf.elf_update(self.elf, cmd))

    def elf_newscn(self):
        scn = _libelf.elf_newscn(self.elf)
        return Elf_ScnDescriptor(_NotNullOrError(scn))

def elf32_fsize(typ, count, version):
    return _libelf.elf32_fsize(typ, count, version)

def _setup():
    _libelf.elf_begin.restype = ctypes.c_void_p
    _libelf.elf_begin.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]

    _libelf.elf_end.restype = ctypes.c_int
    _libelf.elf_end.argtypes = [ctypes.c_void_p]

    _libelf.elf_version.restype = ctypes.c_uint
    _libelf.elf_version.argtypes = [ctypes.c_uint]

    _libelf.elf_kind.restype = ctypes.c_uint
    _libelf.elf_kind.argtypes = [ctypes.c_void_p]

    _libelf.elf32_newehdr.restype = ctypes.POINTER(Elf32_Ehdr)
    _libelf.elf32_newehdr.argtypes = [ctypes.c_void_p]

    _libelf.elf32_newphdr.restype = ctypes.POINTER(Elf32_Phdr)
    _libelf.elf32_newphdr.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

    _libelf.elf_flagphdr.restype = ctypes.c_uint
    _libelf.elf_flagphdr.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_uint]

    _libelf.elf_update.restype = ctypes.c_int
    _libelf.elf_update.argtypes = [ctypes.c_void_p, ctypes.c_int]

    _libelf.elf32_fsize.restype = ctypes.c_size_t
    _libelf.elf32_fsize.argtypes = [ctypes.c_int, ctypes.c_size_t, ctypes.c_uint]

    _libelf.elf_newscn.restype = ctypes.c_void_p
    _libelf.elf_newscn.argtypes = [ctypes.c_void_p]

    _libelf.elf32_getshdr.restype = ctypes.POINTER(Elf32_Shdr)
    _libelf.elf32_getshdr.argtypes = [ctypes.c_void_p]

    _libelf.elf_newdata.restype = ctypes.POINTER(Elf_Data)
    _libelf.elf_newdata.argtypes = [ctypes.c_void_p]

    _libelf.elf_ndxscn.restype = ctypes.c_size_t
    _libelf.elf_ndxscn.argtypes = [ctypes.c_void_p]

    _TrueOrError(_libelf.elf_version(1) != EV_NONE)


if __name__ == "libelf":
    _setup()
