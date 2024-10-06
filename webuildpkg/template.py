###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `template.py`                                                ####
####                                                                       ####
####    Module for handling and parsing template files of the              ####
####    `web-build` utility file standard.                                 ####
####                                                                       ####
###############################################################################
###############################################################################
import traceback
import sys

try:
    from . import shared
    from . import fragment
    from . import parametric
except ImportError:
    import shared
    import fragment
    import parametric


###############################################################################
#                                                                             #
#   Template Constants:                                                       #
#           TEMPLATE_EXTS   -   A priority ordered list of default file       #
#                               extension to append to template file          #
#                               identifiers. `open_template()` will try       #
#                               each in turn until one succeeds.              #
#                                                                             #
###############################################################################
TEMPLATE_EXTS = ["", ".template", ".temp"]


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
#       parse the contents of a template file to the output file.             #
#                                                                             #
###############################################################################
def main(args):
    try:
        infile = open_template(args[1])
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = shared.open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    parse_template(infile, outfile)
    
    infile.close()
    outfile.close()
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_template(name)                                                   #
#                                                                             #
#   Parameters:                                                               #
#       name        -   string: the file name or handle to open as an input   #
#                               file, required.                               #
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
#       `name` using `TEMPLATE_EXTS` unless `name` indicates a standard       #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_template(name):
    if name in shared.STDIOS:
        return sys.stdin
    
    for ext in TEMPLATE_EXTS:
        try:
            f = open(name + ext, 'r')
        except (FileNotFoundError, IsADirectoryError):
            pass
        else:
            return f
    
    raise FileNotFoundError(
        f"Not any such file, tried: "
        f"'{'\', \''.join([name + ext for ext in TEMPLATE_EXTS])}'.")


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_template(infile, outfile, line_no=0)                            #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   an open input file, must be a valid           #
#                               template file, the file to parse, required.   #
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
#       shared.ParseError       -   when the input file is not a correctly    #
#                                   declared template file.                   #
#                                                                             #
#   Description:                                                              #
#       Parses a template file (see README) and writes the results to the     #
#       specified output file.                                                #
#                                                                             #
###############################################################################
def parse_template(infile, outfile, line_no=0):
    if line_no == 0:
        line, line_no = shared.parse_shebang(infile)
        
        _assert_template(shared.parse_command(line, infile.name, line_no),
                         infile.name, line_no, line)
    
    while (line := infile.readline()):
        line_no += 1
        
        try:
            command = shared.parse_command(line, infile.name, line_no)
        except shared.ParseError:
            outfile.write(line)
        else:
            _parse_template_command(
                        command, outfile, infile.name, line_no, line)


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _parse_template_command(                                              #
#                   command, outfile, file_name="", line_no=0, line="")       #
#                                                                             #
#   Parameters:                                                               #
#       command     -   list:   a valid parsed command, the output of         #
#                               `shared.parse_command()` applied to a         #
#                               line of a template file, required.            #
#                                                                             #
#       outfile     -   file:   an open output file, the file to write,       #
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
#       line        -   string: the line from the file, only used for error   #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#   Returns:    None.                                                         #
#                                                                             #
#   Raises:                                                                   #
#       shared.ParseError   -   when the command is not valid, is missing     #
#                               required fields or is not recognized in       #
#                               template files.                               #
#                                                                             #
#       RuntimeError        -   when the command has no readable normal       #
#                               fields.                                       #
#                                                                             #
#   Description:                                                              #
#       Take a command from a template file, check its validity in the        #
#       template file context and delegate to the appropriate function.       #
#                                                                             #
###############################################################################
def _parse_template_command(
                command, outfile, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if cmd and cmd[0] == "" and not cmd[1:]:                    # Comment
        pass
    elif cmd and cmd[0] == "":                                  # Declaration
        raise shared.ParseError(
                f"Template files may not contain declarations.",
                (infile.name, line_no, 1, line.strip()))
    elif cmd and cmd[0] in shared.FILE_IDS and not cmd[1:]:     # No Source
        raise shared.ParseError(
                f"Bad :{cmd[0]} command, must specify source.",
                (infile.name, line_no, 1, line.strip()))
    elif cmd and cmd[0] == shared.TEMPLATE_ID:          # Valid :TEMPLATE
        temfile = open_template(cmd[1])
        
        parse_template(temfile, outfile)
    elif cmd and cmd[0] == shared.FRAGMENT_ID:          # Valid :FRAGMENT
        fragfile = fragment.open_fragment(cmd[1])
        
        fragment.parse_fragment(fragfile, outfile)
    elif cmd and cmd[0] == shared.PARAMETRIC_ID:        # Valid :PARAMETRIC
        parafile = parametric.open_parametric(cmd[1])
        
        params = parametric.parse_parameters(cmd[2:])
        
        parametric.parse_parametric(parafile, outfile, params)
    elif cmd:                                               # Other command
        raise shared.ParseError(f"Unrecognized command :{cmd[0]}.",
                                (infile.name, line_no, 1, line.strip()))
    else:                                       # No command fields (somehow)
        raise RuntimeError(f"  File \"{infile.name}\", line {line_no}\n"
                           f"    {line.strip()}\n"
                           f"  caused a zero-length command to parse.")


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _assert_template(command, file_name="", line_no=0, line="")           #
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
#       shared.ParseError   -   when `command` is not a template file         #
#                               declaration.                                  #
#                                                                             #
#   Description:                                                              #
#       Check that the passed `command` is a template file declaration and    #
#       raise `ParseError` if it is not.                                      #
#                                                                             #
###############################################################################
def _assert_template(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.TEMPLATE_ID:
        raise shared.ParseError(f"Invalid template file declaration.",
                                (file_name, line_no, 1, line.strip()))


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
