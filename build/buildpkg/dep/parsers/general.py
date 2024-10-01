import sys
import io
import re

from . import shared
from . import template
from . import fragment
from . import parametric

from .. import errors


PARSERS = { shared.ID_TEMPLATE   : template.parse_line,
            shared.ID_FRAGMENT   : fragment.parse_line,
            shared.ID_PARAMETRIC : parametric.parse_line }


###### Main Parser ##########
def parse_file(f=None, ftype=None, fpath="", params={}, outfile=sys.stdout):
    f, my_file = _acquire_file(f)
    
    file_type == None
    
    fp = f.tell()
    f.seek(0)
    
    line = f.readline(shared.CHUNK_SIZE)
    
    if shared.SHEBANG.match(line):
        line = f.readline(shared.CHUNK_SIZE)
    
    if shared.COMMAND.match(line):
        command = shared.parse_command(line)[1:-1] # Ignore indent and comment
        
        if len(command) > 1 and command[0] == "" and \
                                command[1] in shared.FILE_IDS:
            file_type = command[1]
    
    if file_type is None:
        errors.file_type_error(
            f"Invalid file declaration: `{line}`: assuming fragment file.",
            mode="WARNING")
        
        file_type = shared.ID_FRAGMENT
        
        outfile.write(line)
    
    while (line := f.readline(shared.CHUNK_SIZE)):
        PARSERS[file_type](line, fpath=fpath, params=params,
                                 outfile=outfile, parser=parse_file)
    
#    read_ftype, first_line = file_type(f)
#    
#    if ftype is not None and \
#       ftype != shared.ID_FRAGMENT and \
#       ftype != read_ftype:
#        errors.file_type_error(
#            f"file \"{f.name}\" does not match requested file type "
#            f"\"{ftype}\".")
#    
#    try:
#        parsed = PARSERS[read_ftype](f, fpath=fpath,
#                                     parse_file=parse_file, params=params)
#    except KeyError:
#        errors.file_type_error(
#            f"file \"{f.name}\" does not match any recognized file type.",
#            mode="WARNING")
#        
#        parsed = fragment.fragment_parser(f, fpath=fpath, prefix=first_line)
    
    if my_file:
        f.close()
    else:
        f.seek(fp)
    
#    return parsed


######### File Checks and Acquisition ################
def _acquire_file(f, context="acquire_file()"):
    if not (isinstance(f, io.TextIOWrapper) or isinstance(f, str)):
        raise TypeError(
            f"{context} needs an open file or a string, got {type(f)}.")
    
    if isinstance(f, io.TextIOWrapper):
        if not f.readable():
            raise ValueError(
                f"File object ({f.name}) is not readable (mode is "
                f"{f.mode!r}. Try opening with mode='r'.")
        
        if not f.seekable():
            raise ValueError(
                f"File object ({f.name}) is not seekable. Try opening with "
                f"mode='r' or copying to a tempfile with mode='w+'.")
        
        return f, False
    
    return open(f, mode='r'), True


def file_type(f=None):
    id_line = f.readline(shared.CHUNK_SIZE)
    
    try:
        id_tag = id_line[:id_line.index(';') + 1].strip()
    except ValueError:
        id_tag = id_line
    
    return id_tag, id_line



##################### End of Code ############################################
#
#
#
##################### End of File ############################################
