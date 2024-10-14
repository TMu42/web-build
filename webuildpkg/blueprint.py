###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `blueprint.py`.                                              ####
####                                                                       ####
####    Summary: Module for handling and parsing blueprint files of the    ####
####             `web-build` utility file standard.                        ####
####                                                                       ####
####    Constants:                                                         ####
####        BLUEPRINT_EXTS  -   list:   Blueprint file extension strs.     ####
####                                                                       ####
####    Methods:                                                           ####
####        main(args)                                                     ####
####                -   Main execution method, not called on import.       ####
####                                                                       ####
####        open_blueprint(name, path)                                     ####
####                -   Open a blueprint file with a given name.           ####
####                                                                       ####
####        parse_blueprint(infile, line_no, file_count)                   ####
####                -   Parse an open blueprint file.                      ####
####                                                                       ####
####        _path(f)       ######################################          ####
####                -   Get a file object's path.                          ####
####                                                                       ####
####        _parse_blueprint_command(command, path, file_count,            ####
####                                          file_name, line_no, line)    ####
####                -   Parse a command from a blueprint file.             ####
####                                                                       ####
####        _assert_blueprint(command, file_name, line_no, line)           ####
####                -   Check command is a blueprint file declaration.     ####
####                                                                       ####
###############################################################################
###############################################################################
import traceback
import sys

try:
    from . import shared
    from . import template
    from . import fragment
    from . import parametric
except ImportError:
    import shared
    import template
    import fragment
    import parametric


###############################################################################
#                                                                             #
#   Blueprint Constants:                                                      #
#           BLUEPRINT_EXTS  -   A priority ordered list of default file       #
#                               extension to append to blueprint file         #
#                               identifiers. `open_blueprint()` will try      #
#                               each in turn until one succeeds.              #
#                                                                             #
###############################################################################
BLUEPRINT_EXTS = ["", ".blueprint", ".blue"]


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       main(args)                                                            #
#                                                                             #
#   Parameters:                                                               #
#       args        -   list:   the argument list as passed at the command    #
#                               line (sys.argv). args[1] will specify the     #
#                               input file, required.                         #
#                                                                             #
#   Returns:    int:    `EXIT_SUCCESS` or an error code.                      #
#                                                                             #
#   Raises:                                                                   #
#       Just about anything...                                                #
#                                                                             #
#   Description:                                                              #
#       The main execution method called if this module is executed rather    #
#       than imported. This method will resolve input and file and parse      #
#       the contents of a blueprint file to produce any specified output.     #
#       files.
#                                                                             #
###############################################################################
def main(args):
    try:
        infile = open_blueprint(args[1])
    except IndexError:
        infile  = sys.stdin
    
    parse_blueprint(infile)
    
    infile.close()
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_blueprint(name, path=None)                                       #
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
#       `name` using `BLUEPRINT_EXTS` unless `name` indicates a standard      #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_blueprint(name, path=None):
    if name in shared.STDINS:
        return sys.stdin
    
    if path and name[0] != '/':
        name = f"{path}/{name}"
    
    for ext in BLUEPRINT_EXTS:
        try:
            f = open(name + ext, 'r')
        except (FileNotFoundError, IsADirectoryError):
            pass
        else:
            return f
    
    raise FileNotFoundError(
        f"Not any such file, tried: "
        f"'{'\', \''.join([name + ext for ext in BLUEPRINT_EXTS])}'.")


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_blueprint(infile, line_no=0, file_count=0)                      #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   an open input file, must be a valid           #
#                               blueprint file, the file to parse,            #
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
#       file_count  -   int:    the number of default files already           #
#                               written, default=0.                           #
#                                                                             #
#   Returns:    int:    the updated file_count.                               #
#                                                                             #
#   Raises:                                                                   #
#       shared.ParseError       -   when the input file is not a correctly    #
#                                   declared blueprint file.                  #
#                                                                             #
#   Description:                                                              #
#       Parses a blueprint file (see README) and recursively processed each   #
#       file invoked by commands, writing their output as specified.          #
#                                                                             #
###############################################################################
def parse_blueprint(infile, line_no=0, file_count=0):
    if line_no == 0:
        line, line_no = shared.parse_shebang(infile)
        
        _assert_blueprint(shared.parse_command(line, infile.name, line_no),
                          infile.name, line_no, line)
    
    while (line := infile.readline()):
        line_no += 1
        
        try:
            command = shared.parse_command(line, infile.name, line_no)
        except shared.ParseError:
            pass
        else:
            file_count = _parse_blueprint_command(
                                    command, _path(infile),
                                    file_count, infile.name, line_no, line)
    
    return file_count


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
#       _parse_blueprint_command(command, path=None, file_count=0,            #
#                                         file_name="", line_no=0, line="")   #
#                                                                             #
#   Parameters:                                                               #
#       command     -   list:   a valid parsed command, the output of         #
#                               `shared.parse_command()` applied to a         #
#                               line of a blueprint file, required.           #
#                                                                             #
#       path        -   string: the path to the file being parsed, used to    #
#                               resolve the names of sourced files for        #
#                               :BLUEPRINT, :TEMPLATE, :FRAGMENT and          #
#                               :PARAMETRIC commands, relative paths are      #
#                               related to the Python working directory       #
#                               which is used if None, "" or ommited,         #
#                               default=None.                                 #
#                                                                             #
#       file_count  -   int:    the number of default files already           #
#                               written, default=0.                           #
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
#   Returns:    int:    the updated file_count.                               #
#                                                                             #
#   Raises:                                                                   #
#       shared.ParseError   -   when the command is not valid, is missing     #
#                               required fields or is not recognized in       #
#                               blueprint files.                              #
#                                                                             #
#       RuntimeError        -   when the command has no readable normal       #
#                               fields.                                       #
#                                                                             #
#   Description:                                                              #
#       Take a command from a blueprint file, check its validity in the       #
#       blueprint file context and delegate to the appropriate function.      #
#                                                                             #
###############################################################################
def _parse_blueprint_command(
        command, path=None, file_count=0, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if cmd and cmd[0] == "" and not cmd[1:]:                    # Comment
        pass
    elif cmd and cmd[0] == "":                                  # Declaration
        raise shared.ParseError(
                f"Blueprint files may not contain declarations.",
                (file_name, line_no, 1, line.strip()))
    elif cmd and cmd[0] in shared.FILE_IDS and not cmd[1:]:     # No Source
        raise shared.ParseError(
                f"Bad :{cmd[0]} command, must specify source.",
                (file_name, line_no, 1, line.strip()))
    elif cmd and cmd[0] == shared.BLUEPRINT_ID:         # Valid :BLUEPRINT
        blufile = open_blueprint(cmd[1], path)
        
        file_count = parse_blueprint(blufile, file_count=file_count)
    elif cmd and cmd[0] == shared.TEMPLATE_ID:          # Valid :TEMPLATE
        temfile = open_template(cmd[1], path)
        
        if cmd[2:] and cmd[2] != "":
            outfile = shared.open_output(cmd[2])
        else:
            outfile = shared.open_output(f"{file_count}.out")
            
            file_count += 1
        
        parse_template(temfile, outfile)
    elif cmd and cmd[0] == shared.FRAGMENT_ID:          # Valid :FRAGMENT
        fragfile = fragment.open_fragment(cmd[1], path)
        
        if cmd[2:] and cmd[2] != "":
            outfile = shared.open_output(cmd[2])
        else:
            outfile = shared.open_output(f"{file_count}.out")
            
            file_count += 1
        
        fragment.parse_fragment(fragfile, outfile)
    elif cmd and cmd[0] == shared.PARAMETRIC_ID:        # Valid :PARAMETRIC
        parafile = parametric.open_parametric(cmd[1], path)
        
        if cmd[2:] and cmd[2] != "":
            outfile = shared.open_output(cmd[2])
        else:
            outfile = shared.open_output(f"{file_count}.out")
            
            file_count += 1
        
        params = parametric.parse_parameters(cmd[3:])
        
        parametric.parse_parametric(parafile, outfile, params)
    elif cmd:                                               # Other command
        raise shared.ParseError(f"Unrecognized command :{cmd[0]}.",
                                (file_name, line_no, 1, line.strip()))
    else:                                       # No command fields (somehow)
        raise RuntimeError(f"  File \"{file_name}\", line {line_no}\n"
                           f"    {line.strip()}\n"
                           f"  caused a zero-length command to parse.")
    
    return file_count


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _assert_blueprint(command, file_name="", line_no=0, line="")          #
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
#       shared.ParseError   -   when `command` is not a blueprint file        #
#                               declaration.                                  #
#                                                                             #
#   Description:                                                              #
#       Check that the passed `command` is a blueprint file declaration and   #
#       raise `ParseError` if it is not.                                      #
#                                                                             #
###############################################################################
def _assert_blueprint(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.BLUEPRINT_ID:
        raise shared.ParseError(f"Invalid blueprint file declaration.",
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
