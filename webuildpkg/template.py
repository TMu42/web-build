###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `template.py`.                                               ####
####                                                                       ####
####    Summary: Module for handling and parsing template files of the     ####
####             `web-build` utility file standard.                        ####
####                                                                       ####
####    Constants:                                                         ####
####        TEMPLATE_EXTS   -   list:   Template file extension strs.      ####
####                                                                       ####
####    Methods:                                                           ####
####        main(args)                                                     ####
####                -   Main execution method, not called on import.       ####
####                                                                       ####
####        open_template(name, path)                                      ####
####                -   Open a template file with a given name.            ####
####                                                                       ####
####        parse_template(infile, outfile, line_no)                       ####
####                -   Parse an open template file.                       ####
####                                                                       ####
####        _path(f)                                                       ####
####                -   Get a file object's path.                          ####
####                                                                       ####
####        _parse_template_command(command, outfile, path,                ####
####                                file_name, line_no, line)              ####
####                -   Parse a command from a template file.              ####
####                                                                       ####
####        _assert_template(command, file_name, line_no, line)            ####
####                -   Check command is a template file declaration.      ####
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
#   Returns:    int:    `EXIT_SUCCESS` or an error code.                      #
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
#       open_template(name, path=None)                                        #
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
#       `name` using `TEMPLATE_EXTS` unless `name` indicates a standard       #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_template(name, path=None):
    if name in shared.STDINS:
        return sys.stdin
    
    if path and name[0] != '/':
        name = f"{path}/{name}"
    
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
        
        command, done = shared.parse_command(line, infile.name, line_no)
        
        while not done:
            line = infile.readline()
            
            line_no += 1
            
            command, done = shared.parse_command(
                                        line, infile.name, line_no, command)
        
        _assert_template(command, infile.name, line_no, line)
    
    command = None
    
    while (line := infile.readline()):
        line_no += 1
        
        try:
            command, done = shared.parse_command(
                                        line, infile.name, line_no, command)
        except shared.ParseError:
            outfile.write(line)
            
            command = None
        else:
            if done:
                _parse_template_command(
                        command, outfile, shared.get_file_path(infile),
                                                infile.name, line_no, line)
                
                command = None


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _path(f)                                                              #
#                                                                             #
#   Parameters:                                                               #
#       f       -   file:   a file from which to extract the path,            #
#                           Required.                                         #
#                                                                             #
#   Returns:    string: the absolute or relative path to the file.            #
#                                                                             #
#   Raises:                                                                   #
#       TypeError   -   when `f` is not a file, obviously.                    #
#                                                                             #
#   Description:                                                              #
#       Extracts and returns the path component from the `name` property of   #
#       a given file, this may be a relative or absolute path depending on    #
#       how the file was opened. Will always be "" if the file was opened     #
#       directly from the local directory or is a numbered or named file      #
#       stream not opened from the file system tree.                          #
#                                                                             #
###############################################################################
def _path(f):
    try:
        return '/'.join(f.name.split('/')[:-1])
    except AttributeError:  # f.name is not a string
        return ""


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _parse_template_command(command, outfile, path=None, file_name="",    #
#                                                       line_no=0, line="")   #
#                                                                             #
#   Parameters:                                                               #
#       command     -   list:   a valid parsed command, the output of         #
#                               `shared.parse_command()` applied to a         #
#                               line of a template file, required.            #
#                                                                             #
#       outfile     -   file:   an open output file, the file to write,       #
#                               required.                                     #
#                                                                             #
#       path        -   string: the path to the file being parsed, used to    #
#                               resolve the names of sourced files for        #
#                               :TEMPLATE, :FRAGMENT and :PARAMETRIC          #
#                               commands, relative paths are related to the   #
#                               Python working directory which is used if     #
#                               None, "" or ommited, default=None.            #
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
            command, outfile, path=None, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if cmd and cmd[0] == "" and not cmd[1:]:                    # Comment
        pass
    elif cmd and cmd[0] == "":                                  # Declaration
        raise shared.ParseError(
                f"Template files may not contain declarations.",
                (file_name, line_no, 1, line.strip()))
    elif cmd and cmd[0] in shared.FILE_IDS and not cmd[1:]:     # No Source
        raise shared.ParseError(
                f"Bad :{cmd[0]} command, must specify source.",
                (file_name, line_no, 1, line.strip()))
    elif cmd and cmd[0] == shared.TEMPLATE_ID:          # Valid :TEMPLATE
        temfile = open_template(cmd[1], path)
        
        parse_template(temfile, outfile)
    elif cmd and cmd[0] == shared.FRAGMENT_ID:          # Valid :FRAGMENT
        fragfile = fragment.open_fragment(cmd[1], path)
        
        fragment.parse_fragment(fragfile, outfile)
    elif cmd and cmd[0] == shared.PARAMETRIC_ID:        # Valid :PARAMETRIC
        parafile = parametric.open_parametric(cmd[1], path)
        
        params = parametric.parse_parameters(cmd[3:], file_name, line_no, line)
        
        parametric.parse_parametric(parafile, outfile, params)
    elif cmd:                                               # Other command
        raise shared.ParseError(f"Unrecognized command :{cmd[0]}.",
                                (file_name, line_no, 1, line.strip()))
    else:                                       # No command fields (somehow)
        raise RuntimeError(f"  File \"{file_name}\", line {line_no}\n"
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
