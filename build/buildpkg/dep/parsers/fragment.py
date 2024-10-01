import tempfile
import sys
import os

from . import shared


def parse_line(line, outfile=sys.stdout, **kwargs):
    pass


def fragment_parser(ffile=None, fpath="", prefix=None, parse_file=None,
                                                                **kwargs):
    parsed_file = tempfile.TemporaryFile(mode='w+')
    
    if prefix is not None:
        parsed_file.write(prefix)
    
    if ffile is not None:
        while (chunk := ffile.read(shared.CHUNK_SIZE)):
            parsed_file.write(chunk)
    
    return [parsed_file]


def resolve_fragment_file(name, path=""):
    priority = [f"{path}{name}",
                f"{path}{name}.fragment",
                f"{path}{name}.frag"]
    
    for fname in priority:
        if os.path.isfile(fname):
            return fname
    
    return None




##################### End of Code ############################################
#
#
#
##################### End of File ############################################
