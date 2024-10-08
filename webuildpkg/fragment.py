###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `fragment.py`                                                ####
####                                                                       ####
####    Summary: Module for handling and parsing fragment files of the     ####
####             `web-build` utility file standard.                        ####
####                                                                       ####
####    Constants:                                                         ####
####        FRAGMENT_EXTS   -   list:   Fragment file extension strs.      ####
####                                                                       ####
####    Methods:                                                           ####
####        main(args)                                                     ####
####                -   Main execution method, not called on import.       ####
####                                                                       ####
####        open_fragment(name, path)                                      ####
####                -   Open a fragment file with a given name.            ####
####                                                                       ####
####        parse_fragment(infile, outfile, line_no)                       ####
####                -   Parse an open fragment file.                       ####
####                                                                       ####
####        _assert_fragment(command, file_name, line_no, line)            ####
####                -   Check command is a fragment file declaration.      ####
####                                                                       ####
###############################################################################
###############################################################################
import traceback
import sys

try:
    from . import shared
except ImportError:
    import shared


###############################################################################
#                                                                             #
#   Fragment Constants:                                                       #
#           FRAGMENT_EXTS   -   A priority ordered list of default file       #
#                               extension to append to fragment file          #
#                               identifiers. `open_fragment()` will try       #
#                               each in turn until one succeeds.              #
#                                                                             #
###############################################################################
FRAGMENT_EXTS = ["", ".fragment", ".frag"]


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       main(args)                                                            #
#                                                                             #
#   Parameters:                                                               #
#       args        -   list:   the argument list as passed at the command    #
#                               line (sys.argv). args[1] will specify the     #
#                               input file and args[2] will specify the       #
#                               output file, required.                        #
#                                                                             #
#   Returns:    int:    `EXIT_SUCCESS` or and error code.                     #
#                                                                             #
#   Raises:                                                                   #
#       Just about anything...                                                #
#                                                                             #
#   Description:                                                              #
#       The main execution method called if this module is executed rather    #
#       than imported. This method will resolve input and output file and     #
#       parse the contents of a fragment file to the output file.             #
#                                                                             #
###############################################################################
def main(args):
    try:
        infile = open_fragment(args[1])
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = shared.open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    parse_fragment(infile, outfile)
    
    infile.close()
    outfile.close()
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_fragment(name)                                                   #
#                                                                             #
#   Parameters:                                                               #
#       name        -   string: the file name or handle to open as an input   #
#                               file, required.                               #
#                                                                             #
#       path        -   string: the context path for name resolution,         #
#                               default=None.                                 #
#                                                                             #
#   Returns:    file:   an open file which can be read from.                  #
#                                                                             #
#   Raises:                                                                   #
#       FileNotFoundError   -   when `name` can't be resolved to a readable   #
#                               regular file (or a standard stream).          #
#                                                                             #
#       PermissionError     -   when `name` resolves to a file which the      #
#                               python instance does not have permission to   #
#                               read.                                         #
#                                                                             #
#   Description:                                                              #
#       Opens and returns a readable file based upon name resolution from     #
#       `name` using `FRAGMENT_EXTS` unless `name` indicates a standard       #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_fragment(name, path=None):
    if name in shared.STDIOS:
        return sys.stdin
    
    if path and name[0] != '/':
        name = f"{path}/{name}"
    
    for ext in FRAGMENT_EXTS:
        try:
            f = open(name + ext, 'r')
        except (FileNotFoundError, IsADirectoryError):
            pass
        else:
            return f
    
    raise FileNotFoundError(
        f"Not any such file, tried: "
        f"'{'\', \''.join([name + ext for ext in FRAGMENT_EXTS])}'.")


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_fragment(infile, outfile, line_no=0)                            #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   an open input file, should be a valid         #
#                               fragment file, the file to parse, required.   #
#                                                                             #
#       outfile     -   file:   an open output file, the file to write,       #
#                               required.                                     #
#                                                                             #
#       line_no     -   int:    the initial line number, default value is     #
#                               the beginning of the file. The file           #
#                               position is not modified, this should         #
#                               be the number of lines already read before    #
#                               the current file position. This is mostly     #
#                               used for error text but also influences       #
#                               whether the file type declaration is          #
#                               checked, default=0.                           #
#                                                                             #
#   Returns:    None.                                                         #
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       Parses a fragment file (see README) and writes the results to the     #
#       specified output file.                                                #
#                                                                             #
###############################################################################
def parse_fragment(infile, outfile, line_no=0):
    if line_no == 0:
        line, line_no = shared.parse_shebang(infile)
        
        try:
            _assert_fragment(shared.parse_command(line, infile.name, line_no),
                             infile.name, line_no, line)
        except shared.ParseError as e:
            traceback.print_exception(e)
            
            outfile.write(line)
    
    while (line := infile.readline()):
        line_no += 1
        
        outfile.write(line)


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _assert_fragment(command, file_name="", line_no=0, line="")           #
#                                                                             #
#   Parameters:                                                               #
#       command     -   list:   a valid parsed command, the output of         #
#                               `shared.parse_command()` applied to the       #
#                               declaration line of a file, required.         #
#                                                                             #
#       file_name   -   string: the name of the file, only used for error     #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#       line_no     -   int:    the line number from the file, only used      #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=0.              #
#                                                                             #
#       line        -   string: the line from the file, only used for error   #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#   Returns:    None.                                                         #
#                                                                             #
#   Raises:                                                                   #
#       shared.ParseError   -   when `command` is not a fragment file         #
#                               declaration.                                  #
#                                                                             #
#   Description:                                                              #
#       Check that the passed `command` is a fragment file declaration and    #
#       raise `ParseError` if it is not.                                      #
#                                                                             #
###############################################################################
def _assert_fragment(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.FRAGMENT_ID:
        raise shared.ParseError(f"Invalid fragment file declaration.",
                                (file_name, line_no, 1, line.strip()))


###############################################################################
#                                                                             #
#   Non-function code to call `main()` when this file is executed rather      #
#   than imported.                                                            #
#                                                                             #
###############################################################################
if __name__ == "__main__":
    sys.exit(main(sys.argv))


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
