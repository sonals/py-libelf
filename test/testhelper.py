"""
 SPDX-License-Identifier: Apache-2.0

 Copyright (C) 2023 Advanced Micro Devices, Inc.

 Helper routines for pylibelf testing
"""

import ctypes
import argparse
import subprocess
import hashlib

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

def parse_command_line(args):
    """ Common command line parser for all tests """
    msg = "Write out a sample ELF file"
    parser = argparse.ArgumentParser(description = msg, exit_on_error = True)
    parser.add_argument("-o", "--output", dest ='filename', nargs = 1)
    parser.add_argument("-r", "--reference", dest ='reference', nargs = '?')
    # strip out the argv[0]
    return parser.parse_args(args[1:])

class ElfStringTable:
    """
    Helper data structure to store and pack strings for ELF which is later
    used to build ELF .shstrtab section
    """
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
