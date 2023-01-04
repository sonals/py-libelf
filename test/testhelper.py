"""
 SPDX-License-Identifier: Apache-2.0

 Copyright (C) 2023 Advanced Micro Devices, Inc.

 Helper routines for pylibelf testing
"""

import argparse
import subprocess
import hashlib

def validate_ELF(elfname, goldname):
    result = subprocess.run(["readelf", "-a", elfname], capture_output = True)
    sig = hashlib.md5(result.stdout).hexdigest()

    if (goldname is None):
        return

    goldsig = None
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
