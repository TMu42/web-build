###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `parametric.py`                                              ####
####                                                                       ####
####    Module for handling and parsing parametric files of the            ####
####    `web-build` utility file standard.                                 ####
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
#   Parametric Constants:                                                     #
#           PARAMETRIC_EXTS     -   A priority ordered list of default file   #
#                                   extension to append to fragment file      #
#                                   identifiers. `open_fragment()` will try   #
#                                   each in turn until one succeeds.          #
#                                                                             #
###############################################################################
PARAMETRIC_EXTS = ["", ".parametric", ".param"]


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
#       parse the contents of a parametric file to the output file.           #
#                                                                             #
###############################################################################
def main(args):
    try:
        infile = open_parametric(args[1])
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = shared.open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    params = _parse_cli_parameters(args[3:])
    
    parse_parametric(infile, outfile, params=params)
    
    infile.close()
    outfile.close()
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_parametric(name)                                                 #
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
#       `name` using `PARAMETRIC_EXTS` unless `name` indicates a standard     #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_parametric(name):
    if name in shared.STDIOS:
        return sys.stdin
    
    for ext in PARAMETRIC_EXTS:
        try:
            f = open(name + ext, 'r')
        except (FileNotFoundError, IsADirectoryError):
            pass
        else:
            return f
    
    raise FileNotFoundError(
        f"Not any such file, tried: "
        f"'{'\', \''.join([name + ext for ext in PARAMETRIC_EXTS])}'.")


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_parametric(infile, outfile, params={}, line_no=0)               #
#                                                                             #
#   Parameters:                                                               #
#       infile      -   file:   an open input file, should be a valid         #
#                               parametric file, the file to parse,           #
#                               required.                                     #
#                                                                             #
#       outfile     -   file:   an open output file, the file to write,       #
#                               required.                                     #
#                                                                             #
#       params      -   dict:   the substitution parameters used for          #
#                               parsing the parametric file. Each parameter   #
#                               must be a key in the dict, the value is the   #
#                               substitution, default={}.                     #
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
#       Parses a parametric file with a set of parameter substitutions (see   #
#       README) and writes the results to the specified output file.          #
#                                                                             #
###############################################################################
def parse_parametric(infile, outfile, params={}, line_no=0):
    if line_no == 0:
        line, line_no = shared.parse_shebang(infile)
        
        _assert_parametric(shared.parse_command(line, infile.name, line_no),
                           infile.name, line_no, line)
    
    while (line := infile.readline()):
        line_no += 1
        
        try:
            _param(shared.parse_command(line, infile.name, line_no),
                   params, infile.name, line_no, line) 
        except shared.ParseError:
            outfile.write(
                _parse_parametric_line(line, params, infile.name, line_no))
        except ValueError as e:
            traceback.print_exception(e)

###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _param(command, params, file_name="", line_no=0, line="")             #
#                                                                             #
#   Parameters:                                                               #
#       command     -   list:   a valid parsed command, the output of         #
#                               `shared.parse_command()` applied to a         #
#                               parameter declaration line of a file,         #
#                               required.                                     #
#                                                                             #
#       params      -   dict:   the substitution parameters used for          #
#                               parsing the parametric file, required.        #
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
#       ValueError      -   when the command is not a parameter               #
#                           declaration.                                      #
#                                                                             #
#       shared.ParameterError                                                 #
#                       -   when the parameter is declared as required but    #
#                           it is missing form `params`.                      #
#                                                                             #
#   Description:                                                              #
#                                                                             #
###############################################################################
def _param(command, params, file_name="", line_no=0, line=""):
    cmd = command[1:-1] + ["", "", "", ""]
    
    if cmd[0:2] != ["", "PARAM"]:
        raise ValueError(f"Command {command} is not a parameter declaration.")
    
    if cmd[2] in params.keys():
        return
    
    if cmd[3] == "True" and cmd[4] == "":
        raise shared.ParameterError(f"Missing required parameter {cmd[2]}",
                                    (file_name, line_no, 1, line.strip()))
    elif cmd[3] == "True":
        traceback.print_exception(shared.ParameterError(
            f"Missing required parameter {cmd[2]} with default value "
            f"'{cmd[4]}'",
            (file_name, line_no, 1, line.strip())))
    elif cmd[3] == "" and cmd[4] == "":
        traceback.print_exception(shared.ParameterError(
            f"Missing parameter '{cmd[2]}', (default='')",
            (file_name, line_no, 1, line.strip())))
    
    params[cmd[2]] = cmd[4]


def _assert_parametric(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.PARAMETRIC_ID:
        raise shared.ParseError(f"Invalid parametric file declaration.",
                                (file_name, line_no, 1, line.strip()))


def _parse_parametric_line(line, params, file_name="", line_no=0):
    in_macro, transition, escape = False, False, False
        
    out_line = ""
    macro = ""
    
    pos = 0
    
    for c in line:
        pos += 1
        
        d, e, escape = _escape_state_machine(c, escape)
        
        out_line, macro, in_macro, transition \
            = _macro_state_machine(
                    d, e, in_macro, transition, out_line, macro, params,
                    file_name=file_name, line_no=line_no, pos=pos, line=line)
    
    return out_line


def _escape_state_machine(c, escape):
    if escape:
        d = ''
        e = c
        
        escape = False
    elif c == '\\':
        d = ''
        e = ''
        
        escape = True
    else:
        d = c
        e = c
    
    return d, e, escape


def _macro_state_machine(d, e, in_macro, transition, out_line, macro, params,
                         file_name="", line_no=0, pos=1, line=None):
    if in_macro and transition and d == '>':
        in_macro, transition = False, False
        
        out_line += _get_parameter(params, macro, file_name=file_name,
                                   line_no=line_no, pos=pos, line=line)
    elif in_macro and transition:
        transition = False
        
        macro += (']' + e)
    elif in_macro and d == ']':
        transition = True
    elif in_macro:
        macro += e
    elif transition and d == '[':
        in_macro, transition = True, False
        
        macro = ""
    elif transition:
        transition = False
        
        out_line += ('<' + e)
    elif d == '<':
        transition = True
    else:
        out_line += e
    
    return out_line, macro, in_macro, transition


def _get_parameter(params, param, file_name="", line_no=0, pos=1, line=None):
    if line == None:
        line = param
    
    try:
        return params[param]
    except KeyError:
        traceback.print_exception(shared.ParameterError(
                                f"Missing parameter '{param}', (default='')",
                                (file_name, line_no, pos, line)))
        
        params[param] = ""
        
        return ""


def _parse_cli_parameters(args):
    params = {}
    
    for arg in args:
        escape = False
        
        idx = 0
        
        name_val = ["", ""]
        
        for c in arg:
            if escape:
                name_val[idx] += c
                
                escape = False
            elif c == '\\':
                escape = True
            elif c == '=':
                idx += 1
            else:
                name_val[idx] += c
        
        if idx == 1:
            params[name_val[0]] = name_val[1]
    
    return params


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
