#!/usr/bin/env python

# Copyright (c) 2011 Daniel Poelzleithner <poelzleithner @ b1-systems.de>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#   * Neither the name of Pioneers of the Inevitable, Songbird, nor the names
#     of its contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from optparse import OptionParser
import subprocess
import os, os.path
import sys

VERSION = "0.1"

usage = "usage: %prog [options] ofafile\nConvert applience and virtual images into useful ones"
parser = OptionParser(usage=usage, version=VERSION)
parser.add_option("-f", "--format", dest="format",
                  help="convert info given format (default: qcow2)", default="qcow2")

(options, args) = parser.parse_args()


def convert_img(path, target_format="qcow2"):
    """
    convert img to target format
    """
    dir = os.path.dirname(path)
    basename = os.path.basename(path)
    base,ext = os.path.splitext(basename)
    
    print "convert %s into useful format" %path

    # generate itermediet vdi
    if ext.lower() != ".vdi":
        vdiout = os.path.join(dir, base + ".vdi")
        if os.path.exists(vdiout):
            print "file exists, skipping"
        else:
            print "converting to VDI (intermediat): %s" %vdiout
            subprocess.check_call(["VBoxManage", "clonehd", path, "--format", "VDI", vdiout])

    if target_format.lower() != "vdi":
        target_out = os.path.join(dir, base + "." + target_format)
        print "converting to target format: %s" %target_out
        subprocess.check_call(["qemu-img", "convert", "-f", "vdi", vdiout, "-O", target_format, target_out])
        return target_out
    else:
        return vdiout

def unpack_ofa(path):
    nd = os.path.join(os.getcwd(), os.path.dirname(path), os.path.splitext(os.path.basename(path))[0])
    print "create target directory", nd
    rpath = os.path.join(os.getcwd(), path)
    if not os.path.exists(nd):
        os.mkdir(nd)
    print "unpack applience"
    subprocess.check_call(["tar", "xvf", rpath], cwd=nd)
    files = os.listdir(nd)
    for file in files:
        x = os.path.splitext(file)
        if len(x) < 2: continue
        if x[-1].lower() == '.vmdk':
            convert_img(os.path.join(nd, file), options.format)


def main():
    if len(args) != 1:
        parser.print_usage()
        sys.exit(1)
    
    try:
       ext = os.path.splitext(args[0])[1]
    except IndexError:
        print "can't determine type of image"
        sys.exit(2)

    print ext
    if ext == ".ofa" or ext == ".ova":
       unpack_ofa(args[0])

    elif ext == ".vdi":
       convert_img(args[0], options.format)

    else:
        print "don't know this image type"
        sys.exit(3)
       

    


if __name__ == '__main__':
    main()

