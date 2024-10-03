###############################################################################
###############################################################################
####                                                                       ####
####    File: `shared.py`                                                  ####
####                                                                       ####
####    Shared properties for package `webuildpkg` which provides file     ####
####    parsing and other utilities for handling `web-build` files         ####
####                                                                       ####
###############################################################################
###############################################################################
import sys


###############################################################################
#                                                                             #
#   Shared Constants:                                                         #
#           STDIOS          -   A list of strings which indicate that an      #
#                               input or output stream should be mapped to    #
#                               stdin or stdout respectively, rather than     #
#                               to a regular file.                            #
#                                                                             #
#           FRAGMENT_ID     -   The file and command ID string for fragment   #
#                               files. This appears in the declaration        #
#                               command (file identifier) and also the        #
#                               name (field 1) of the command for invoking    #
#                               these files.                                  #
#                                                                             #
#           PARAMETRIC_ID   -   The file and command ID string for            #
#                               parametric files. This appears in the         #
#                               declaration command (file identifier) and     #
#                               also the name (field 1) of the command for    #
#                               invoking these files.                         #
#                                                                             #
###############################################################################
STDIOS = ['-', '']

FRAGMENT_ID   = "FRAGMENT"
PARAMETRIC_ID = "PARAMETRIC"


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
#                               file, required.                               #
#                                                                             #
#   Returns:    file:   an open file which can be written to.                 #
#                                                                             #
#   Raises:                                                                   #
#       Anything that builtin `open(name, 'w')` might raise.                  #
#                                                                             #
#   Description:                                                              #
#       Opens and returns a writable file with the provided `name` unless     #
#       `name` indicates that the standard stream should be used, i.e.        #
#       `name` is either "" or "-". If the standard stream is indicated,      #
#       sys.stdout is returned.                                               #
#                                                                             #
###############################################################################
def open_output(name):
    if name in STDIOS:
        return sys.stdout
    
    return open(name, 'w')


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
#       parse_command(line, file_name="", line_no=0)                          #
#                                                                             #
#   Parameters:                                                               #
#       line        -   string: the line containing the command to parse,     #
#                               required.                                     #
#                                                                             #
#       file_name   -   string: the name of the file, only used for error     #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#       line_no     -   int:    the line number from the file, only used      #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=0.              #
#                                                                             #
#   Returns:    list:   a list of the command fields as strings.              #
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
def parse_command(line, file_name="", line_no=0):
    command = [""]
    
    colon, semicolon, escape = False, False, False
    
    for c in line:
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
    elif command[0].strip() or (line + '\\').index('\\') < line.index(':'):
        raise ParseError(
                f"Non whitespace character preceeding command initiator ':'.",
                (file_name, line_no, line.strip().index(':'), line.strip()))
    elif not semicolon:
        raise ParseError(f"Command terminator ';' missing.",
                         (file_name, line_no, len(line.strip()), line.strip()))
    
    return command


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
