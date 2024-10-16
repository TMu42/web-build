###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `shared.py`.                                                 ####
####                                                                       ####
####    Summary: Shared properties for package `webuildpkg` which          ####
####             provides file parsing and other utilities for handling    ####
####             `web-build` files.                                        ####
####                                                                       ####
####    Constants:                                                         ####
####        STDINS          -   list:   STDIN indicator strings.           ####
####        STDOUTS         -   list:   STDOUT indicator strings.          ####
####        BLUEPRINT_ID    -   string: Indicates blueprint file.          ####
####        TEMPLATE_ID     -   string: Indicates template file.           ####
####        FRAGMENT_ID     -   string: Indicates fragment file.           ####
####        PARAMETRIC_ID   -   string: Indicates parametric file.         ####
####        FILE_IDS        -   list:   The file IDs above in a list.      ####
####                                                                       ####
####    Classes:                                                           ####
####        ParseError      -   Exception for file syntax errors.          ####
####        ParameterError  -   Exception for missing parameter errors.    ####
####                                                                       ####
####    Methods:                                                           ####
####        open_output(name)                                              ####
####                -   Provide an output file for a given name.           ####
####                                                                       ####
####        open_input(name)                                               ####
####                -   Provide an input file for a given name.            ####
####                                                                       ####
####        get_file_type(infile, outfile)                                 ####
####                -   Get the file type of a web-build file.             ####
####                                                                       ####
####        get_file_path(f)                                               ####
####                -   Get the path to a file( name)'s parent dir.        ####
####                                                                       ####
####        parse_shebang(infile)                                          ####
####                -   Get the first file line, ignoring a shebang.       ####
####                                                                       ####
####        parse_command(line, file_name, line_no, base_command)          ####
####                -   Convert a file line into a canonical command.      ####
####                                                                       ####
###############################################################################
###############################################################################
import traceback
import pathlib
import sys


###############################################################################
#                                                                             #
#   Shared Constants:                                                         #
#           STDINS          -   A list of strings which indicate that an      #
#                               input stream should be mapped to stdin,       #
#                               rather than to a regular file.                #
#                                                                             #
#           STDOUTS         -   A list of strings which indicate that an      #
#                               input stream should be mapped to stdout,      #
#                               rather than to a regular file.                #
#                                                                             #
#           BLUEPRINT_ID    -   The file and command ID string for            #
#                               blueprint files. This appears in the          #
#                               declaration command (file identifier) and     #
#                               also the name (field 1) of the command for    #
#                               invoking blueprint files.                     #
#                                                                             #
#           TEMPLATE_ID     -   The file and command ID string for template   #
#                               files. This appears in the declaration        #
#                               command (file identifier) and also the        #
#                               name (field 1) of the command for invoking    #
#                               template files.                               #
#                                                                             #
#           FRAGMENT_ID     -   The file and command ID string for fragment   #
#                               files. This appears in the declaration        #
#                               command (file identifier) and also the        #
#                               name (field 1) of the command for invoking    #
#                               fragment files.                               #
#                                                                             #
#           PARAMETRIC_ID   -   The file and command ID string for            #
#                               parametric files. This appears in the         #
#                               declaration command (file identifier) and     #
#                               also the name (field 1) of the command for    #
#                               invoking parametric files.                    #
#                                                                             #
#           FILE_IDS        -   A list of all valid file IDs, those           #
#                               specified above.                              #
#                                                                             #
###############################################################################
STDINS  = ['-', "<stdin>"]
STDOUTS = ['-', "<stdout>"]

BLUEPRINT_ID  = "BLUEPRINT"
TEMPLATE_ID   = "TEMPLATE"
FRAGMENT_ID   = "FRAGMENT"
PARAMETRIC_ID = "PARAMETRIC"

FILE_IDS = [ BLUEPRINT_ID,
             TEMPLATE_ID,
             FRAGMENT_ID,
             PARAMETRIC_ID ]


###############################################################################
#                                                                             #
#   Exception Classes:                                                        #
#           ParseError  -   Like a Syntax Error for any of the file formats   #
#                           supported by this package. Any file parser or     #
#                           component of a file parser may raise (or print)   #
#                           this exception to indicate an error in the file   #
#                           syntax.                                           #
#                                                                             #
#           ParameterError                                                    #
#                       -   Although this extends `SyntaxError`, its use is   #
#                           more similar to `NameError`. It is used by the    #
#                           parser for parametric files, and its components   #
#                           to indicate missing parameters.                   #
#                                                                             #
###############################################################################
class ParseError(SyntaxError): pass
class ParameterError(SyntaxError): pass


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_output(name)                                                     #
#                                                                             #
#   Parameters:                                                               #
#       name        -   string: the file name or handle to open as an         #
#                               output file, required.                        #
#                                                                             #
#   Returns:    file:   an open file which can be written to.                 #
#                                                                             #
#   Raises:                                                                   #
#       Anything that builtin `open(name, 'w')` might raise.                  #
#                                                                             #
#   Description:                                                              #
#       Opens and returns a writable file with the provided `name` unless     #
#       `name` indicates that the stdout should be used, i.e. `name` is '-'   #
#       or "<stdout>", in which case sys.stdout is returned.                  #
#                                                                             #
###############################################################################
def open_output(name):
    pathlib.Path(get_file_path(name)).mkdir(parents=True, exist_ok=True)
    
    if name in STDOUTS:
        return sys.stdout
    
    return open(name, 'w')


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_input(name)                                                      #
#                                                                             #
#   Parameters:                                                               #
#       name        -   string: the file name or handle to open as an input   #
#                               file, required.                               #
#                                                                             #
#   Returns:    file:   an open file which can be read from.                  #
#                                                                             #
#   Raises:                                                                   #
#       Anything that builtin `open(name, 'r')` might raise.                  #
#                                                                             #
#   Description:                                                              #
#       Opens and returns a readable file with the provided `name` unless     #
#       `name` indicates that the stdin should be used, i.e. `name` is '-'    #
#       or "<stdin>", in which case sys.stdin is returned.                    #
#                                                                             #
###############################################################################
def open_input(name):
    if name in STDINS:
        return sys.stdin
    
    return open(name, 'r')


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       get_file_type(infile, outfile=None)                                   #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   the open input file to check the file type    #
#                               of, required.                                 #
#                                                                             #
#       outfile:    -   file:   the open output file to write any             #
#                               pass-through to, default=None.                #
#                                                                             #
#   Returns:    string: the file identifier extracted from the file           #
#                       declaration line if present and valid, otherwise      #
#                       the default (`FRAGMENT_ID`).                          #
#                                                                             #
#               int:    the line number of the last line parsed by this       #
#                       method.                                               #
#                                                                             #
#   Raises:                                                                   #
#       Usually nothing unless there is a problem with the call.              #
#                                                                             #
#   Description:                                                              #
#       Extracts and returns the file identifier from an open input file if   #
#       it has a valid web-build header, otherwise, assumes it is a           #
#       fragment file and echos the read line to outfile (if not None),       #
#       returning the fragment file identifier `FRAGMENT_ID`.                 #
#                                                                             #
###############################################################################
def get_file_type(infile, outfile=None):
    line, line_no = parse_shebang(infile)
    
    try:
        file_dec = parse_command(line, infile.name, line_no)
        
        file_type = file_dec[2]
    except (ParseError, IndexError) as e:
        valid = False
    else:
        valid = True
    
    if (not valid) or file_type not in FILE_IDS:
        traceback.print_exception(ParseError(
                                    f"Invalid file declaration '{line}', "
                                    f"assuming fragment file.",
                                    (infile.name, line_no, 1, line.strip())))
        
        if outfile is not None:
            outfile.write(line)
        
        file_type = FRAGMENT_ID
    
    return file_type, line_no


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       get_file_path(f)                                                      #
#                                                                             #
#   Parameters:                                                               #
#       f       -   file/string:    a file (or file name) from which to       #
#                                   extract the parent directory path,        #
#                                   Required.                                 #
#                                                                             #
#   Returns:    string: the absolute or relative path to the file.            #
#                                                                             #
#   Raises:                                                                   #
#       TypeError   -   when `f` is not a file, obviously.                    #
#                                                                             #
#   Description:                                                              #
#       Extracts and returns the path component from the `name` property of   #
#       a given file (or a provided file name if string), this may be a       #
#       relative or absolute path depending on how the file was opened or     #
#       the nature of the file name. Will always be "" if the file was        #
#       opened directly from the local directory or is a numbered or named    #
#       file stream not opened from the file system tree.                     #
#                                                                             #
###############################################################################
def get_file_path(f):
    try:
        path = f.name
    except AttributeError:  # f is not a file, try string
        path = f
    
    try:
        return '/'.join(path.split('/')[:-1])
    except AttributeError:  # path is not a string
        return ""


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_shebang(infile)                                                 #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   an open, readable file whose current file     #
#                               position pointer is at the beginning of the   #
#                               logical file, required.                       #
#                                                                             #
#   Returns:    string, int:    The first non-shebang line and the line       #
#                               number of this line (1 or 2).                 #
#                                                                             #
#   Raises:                                                                   #
#       IOError     -   when `infile` is not readable.                        #
#                                                                             #
#   Description:                                                              #
#       Read from an open file, the first line and if it is a shebang,        #
#       discard and read the second line. Return the full line and the line   #
#       number (either 1 or 2).                                               #
#                                                                             #
###############################################################################
def parse_shebang(infile):
    if (line := infile.readline()) and line[0:2] == "#!":
        return infile.readline(), 2
    
    return line, 1


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_command(line, file_name="", line_no=0, base_command=None)       #
#                                                                             #
#   Parameters:                                                               #
#       line            -   string: the line containing the command to        #
#                                   parse, required.                          #
#                                                                             #
#       file_name       -   string: the name of the file, only used for       #
#                                   error messages so may safely be           #
#                                   omitted if this is not required,          #
#                                   default="".                               #
#                                                                             #
#       line_no         -   int:    the line number from the file, only       #
#                                   used error messages so may safely be      #
#                                   omitted if this is not required,          #
#                                   default=0.                                #
#                                                                             #
#       base_command    -   list:   if continuing command parsing over a      #
#                                   line break, the command as parsed thus    #
#                                   far, default=None.                        #
#                                                                             #
#   Returns:    list:   a list of the command fields as strings.              #
#               bool:   is the command complete or does the next line need    #
#                       parsing as part of the same command.                  #
#                                                                             #
#   Raises:                                                                   #
#       ParseError  -   when `line` is not a properly formed command.         #
#                                                                             #
#   Description:                                                              #
#       Parses a line containing a valid command syntax and returns that      #
#       command as a list of strings. Each element of the list will be the    #
#       contents of the command field matching its index. Command fields      #
#       are 1-based so the zeroth entry is reserved to contain the indent     #
#       whitespace. The only other exception is the last entry which will     #
#       contain the comment. This representation is canonical and all         #
#       commands should be passed between functions in this form. To handle   #
#       just the functional content of the command, simply use                #
#       `command[1:-1]` but never pass the command in this form as            #
#       functions will assume that the indent and comment are present and     #
#       truncate them.                                                        #
#                                                                             #
###############################################################################
def parse_command(line, file_name="", line_no=0, base_command=None):
    if base_command is not None:
        command, line, colon = base_command, line.lstrip(), True
    else:
        command, colon = [""], False
    
    semicolon, escape = False, False
    
    for c in line.split('\n')[0]:
        if escape or semicolon:
            command[-1] += c
            
            escape = False
        elif c == '\\':
            escape = True
        elif c == ':':
            colon = True
            
            command += [""]
        elif c == ';':
            semicolon = True
            
            command += [""]
        else:
            command[-1] += c
    
    if not colon:
        raise ParseError(f"Command initiator ':' missing.",
                         (file_name, line_no, 1, line.strip()))
    elif base_command is None \
    and (command[0].strip() or (line + '\\').index('\\') < line.index(':')):
        raise ParseError(
                f"Non whitespace character preceeding command initiator ':'.",
                (file_name, line_no, line.strip().index(':'), line.strip()))
    elif (not semicolon) and (not escape):
        raise ParseError(f"Command terminator ';' missing.",
                         (file_name, line_no, len(line.strip()), line.strip()))
    
    return command, not escape


###############################################################################
#                                                                             #
#   End of Code                                                               #
#                                                                             #
###############################################################################
#
#
#
###############################################################################
#                                                                             #
#   End of File                                                               #
#                                                                             #
###############################################################################
