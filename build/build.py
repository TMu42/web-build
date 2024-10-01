#! /usr/bin/python


import tempfile
import sys
import re

from buildpkg import parsers
from buildpkg import errors


def main(args):
    infile, inpath, outfile = _acquire_files(args)
    
    parsers.parse_file(infile, fpath=inpath, outfile=outfile)
    
#    for pfile in parsed:
#        pfile.seek(0)
#        
#        while (chunk := pfile.read(parsers.CHUNK_SIZE)):
#            outfile.write(chunk)
#        
#        pfile.close()
    
    infile.close()
    outfile.close()


def _acquire_files(args):
    if len(args) < 2 or args[1] == '-':
        infile = tempfile.TemporaryFile(mode='w+')
        
        while (chunk := sys.stdin.read(parsers.CHUNK_SIZE)):
            infile.write(chunk)
        
        infile.seek(0)
        
        inpath = "./"
    else:
        infile = open(args[1], 'r')
        inpath = '/'.join(args[1].split('/')[:-1] + [''])
    
    if len(args) < 3 or args[2] == '-':
        outfile = sys.stdout
    else:
        outfile = open(args[2], 'w')
    
    return infile, inpath, outfile


if __name__ == "__main__":
    sys.exit(main(sys.argv))


##################### End of Code ############################################
#
#
#
##################### End of File ############################################
