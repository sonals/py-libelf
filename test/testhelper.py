"""
 SPDX-License-Identifier: MIT

 Copyright (C) 2023 Advanced Micro Devices, Inc.

 Helper routines for pylibelf testing
"""

import ctypes
import argparse
import subprocess
import hashlib

import pylibelf

def validate_ELF(elfname, goldname):
    """
    Read the ELF file headers using binutils version of ``readelf`` (not ``eu-readelf``)
    and compare it with the golden version provided
    """
    result = subprocess.run(["readelf", "-a", elfname], capture_output = True,
                            check = True)
    sig = hashlib.md5(result.stdout).hexdigest()

    if (goldname is None):
        return

    goldsig = None
    with open(goldname, "rb") as goldhandle:
        gold = goldhandle.read()
        goldsig = hashlib.md5(gold).hexdigest()
    assert(sig == goldsig), "ELF headers mismatch for " + elfname

def dump_section_contents(scn):
    data = ctypes.string_at(scn.contents.d_buf, scn.contents.d_size)
    for index in range(scn.contents.d_size):
        if (index % 16 == 0):
            print()
        print(f"{hex(data[index])} ", end = '')

    print()

def read_ELF(elfname):
    """
    Read the ELF file headers and display details
    """
    melf = pylibelf.libelf.ElfDescriptor.fromfile(elfname, pylibelf.libelf.Elf_Cmd.ELF_C_READ)
    ehdr = melf.elf32_getehdr()

    curr = melf.elf_getscn(ehdr.contents.e_shstrndx)
    curr_shdr = curr.elf32_getshdr()
    curr_data = curr.elf_getdata()
    assert(curr_data.contents.d_size == curr_shdr.contents.sh_size)
    strtab = ElfStringTable(curr_data.contents.d_buf, curr_data.contents.d_size)
    curr = melf.elf_nextscn(None)

    index = 0
    while (curr != None):
        curr_shdr = curr.elf32_getshdr()
        curr_name = curr_shdr.contents.sh_name
        name = strtab.get(curr_name)
        scn_data = curr.elf_getdata()
        assert(scn_data.contents.d_size == curr_shdr.contents.sh_size)
        print(f"[ {index}] {name} {hex(curr_shdr.contents.sh_size)} {hex(curr_shdr.contents.sh_addralign)}")
        dump_section_contents(scn_data)
        curr = melf.elf_nextscn(curr)
        index += 1


def parse_command_line(args):
    """ Common command line parser for all tests """
    msg = "Write out a sample ELF file"
    parser = argparse.ArgumentParser(description = msg, exit_on_error = True)
    parser.add_argument("-o", "--output", dest ='filename', nargs = 1)
    parser.add_argument("-r", "--reference", dest ='reference', nargs = '?')
    parser.add_argument("-d", "--decompile", dest ='decompile', nargs = 1)
    # strip out the argv[0]
    return parser.parse_args(args[1:])

class ElfStringTable:
    """
    Helper data structure to store and pack strings for ELF which is later
    used to build ELF .shstrtab section
    """
    def __init__(self, data = None, size = 0):
        self._size = size
        self._syms = []
        self._data = None
        if (data == None):
            return
        self._data = ctypes.string_at(data, size)
        # Populate our syms list
        pos = 0
        while (pos < size):
            item = self.get(pos)
            self._syms.append(item)
            pos += len(item)
            # Go past the null char
            pos += 1

    # Support len() operator on the table e.g. len(mystab)
    def __len__(self):
        return len(self._syms)

    # Support indexing into the table e.g. mystab[i]
    def __getitem__(self, index):
        return self._syms[index]

    def add(self, item):
        pos = self._size
        self._syms.append(item)
        self._size += (len(item) + 1)
        return pos

    def _pack(self, arr, index):
        subdata = ctypes.cast(ctypes.addressof(self._data) + index, ctypes.c_void_p)
        ctypes.memmove(subdata, arr, len(arr))
        index += len(arr)
        return index

    def packsyms(self):
        self._data = ctypes.create_string_buffer(self._size)
        index = 0
        for item in self._syms:
            arr = bytes(item, "utf-8")
            index = self._pack(arr, index)
            self._data[index] = b'\0'
            index += 1
        return self._data

    def get(self, pos):
        assert(pos < self._size), f"Illegal offset into table storage"
        item = ctypes.string_at(self._data[pos:])
        return item.decode("utf-8")

    def space(self):
        return self._size

    def __str__(self):
        return f"{self._syms}\n{self._data}"

# TODO: Move to python Generics so can use the same class for
# ElfRelaTable and ElfSymbolTable

class ElfSymbolTable(ElfStringTable):
    """
    Helper data structure to store and pack Elf32_Sym which is later
    used to build ELF .dynsym section
    """
    def __init__(self, data = None, size = 0):
        super().__init__(data, size)
        if (self._data == None):
            return
        # Populate our syms list
        pos = 0
        while (pos < self._size):
            self._syms.append(self.get(pos))
            pos += ctypes.sizeof(pylibelf.elf.Elf32_Sym)

    def add(self, item):
        pos = self._size
        self._syms.append(item)
        assert(ctypes.sizeof(item) == ctypes.sizeof(pylibelf.elf.Elf32_Sym)), f"Illegal item {item}"
        self._size += ctypes.sizeof(item)
        return pos

    def packsyms(self):
        self._data = ctypes.create_string_buffer(self._size)
        index = 0
        for item in self._syms:
            arr = bytes(item)
            index = self._pack(arr, index)
        return self._data

    def get(self, pos):
        assert(pos < self._size), f"Illegal offset into table storage"
        item = pylibelf.elf.Elf32_Sym.from_address(ctypes.addressof(self._data) + pos)
        return item

class ElfRelaTable(ElfStringTable):
    """
    Helper data structure to store and pack Elf32_Rela which is later
    used to build ELF .rela.dyn section
    """
    def __init__(self, data = None, size = 0):
        super().__init__(data, size)
        if (self._data == None):
            return
        # Populate our syms list
        pos = 0
        while (pos < self._size):
            self._syms.append(self.get(pos))
            pos += ctypes.sizeof(pylibelf.elf.Elf32_Rela)

    def add(self, item):
        pos = self._size
        self._syms.append(item)
        assert(ctypes.sizeof(item) == ctypes.sizeof(pylibelf.elf.Elf32_Rela)), f"Illegal item {item}"
        self._size += ctypes.sizeof(item)
        return pos

    def packsyms(self):
        self._data = ctypes.create_string_buffer(self._size)
        index = 0
        for item in self._syms:
            arr = bytes(item)
            index = self._pack(arr, index)
        return self._data

    def get(self, pos):
        assert(pos < self._size), f"Illegal offset into table storage"
        item = pylibelf.elf.Elf32_Rela.from_address(ctypes.addressof(self._data) + pos)
        return item
