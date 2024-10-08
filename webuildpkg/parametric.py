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
#                                   extension to append to parametric file    #
#                                   identifiers. `open_parametric()` will     #
#                                   try each in turn until one succeeds.      #
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
#                               output file, additional arguments may         #
#                               specify parameter bindings, required.         #
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
    
    params = parse_parameters(args[3:])
    
    parse_parametric(infile, outfile, params=params)
    
    infile.close()
    outfile.close()
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_parametric(name, path=None)                                      #
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
#       `name` using `PARAMETRIC_EXTS` unless `name` indicates a standard     #
#       stream (see `shared.open_output()`). If the standard stream is        #
#       indicated, sys.stdin is returned.                                     #
#                                                                             #
###############################################################################
def open_parametric(name, path=None):
    if name in shared.STDIOS:
        return sys.stdin
    
    if path and name[0] != '/':
        name = f"{path}/{name}"
    
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
#       shared.ParseError       -   when the input file is not a correctly    #
#                                   declared parametric file.                 #
#                                                                             #
#       shared.ParameterError   -   when a required parameter is not          #
#                                   provided in `params`.                     #
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
#       Take a parameter declaration command, check if it has been supplied   #
#       at invocation (or by a previous declaration), raise any errors or     #
#       warnings per the declaration parameters (see README) and update the   #
#       parameter list as needed.                                             #
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


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _assert_parametric(command, file_name="", line_no=0, line="")         #
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
#       shared.ParseError   -   when `command` is not a parametric file       #
#                               declaration.                                  #
#                                                                             #
#   Description:                                                              #
#       Check that the passed `command` is a parametric file declaration      #
#       and raise `ParseError` if it is not.                                  #
#                                                                             #
###############################################################################
def _assert_parametric(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.PARAMETRIC_ID:
        raise shared.ParseError(f"Invalid parametric file declaration.",
                                (file_name, line_no, 1, line.strip()))


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _parse_parametric_line(line, params, file_name="" line_no=0)          #
#                                                                             #
#   Parameters:                                                               #
#       line        -   string: a line from the file being parsed,            #
#                               required.                                     #
#                                                                             #
#       params      -   dict:   the substitution parameters used for          #
#                               parsing the parametric file, default={}.      #
#                                                                             #
#       file_name   -   string: the name of the file, only used for error     #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#       line_no     -   int:    the line number from the file, only used      #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=0.              #
#                                                                             #
#   Returns:    string: the parsed line after escapes and substitutions       #
#                       have been applied to the input.                       #
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       Parses a single line from a parametric file with a set of parameter   #
#       substitutions (see README). Escapes are correctly processed and       #
#       parameter substitutions are performed. This method assumes that the   #
#       line is not a valid command so this should have been checked first    #
#       (with `shared.parse_command()` and `_param()`. Note that this         #
#       method makes use of another two helper methods which provide the      #
#       state-machines for line parsing: `_escape_state_machine()` and        #
#       `_macro_state_machine()`.                                             #
#                                                                             #
###############################################################################
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


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _escape_state_machine(c, escape)                                      #
#                                                                             #
#   Parameters:                                                               #
#       c           -   string: a single character of line input,             #
#                               required.                                     #
#                                                                             #
#       escape      -   bool:   the "current" state of this state-machine,    #
#                               required.                                     #
#                                                                             #
#   Returns:                                                                  #
#       string: the control character output to the next state-machine.       #
#       string: the output character output to the next state-machine.        #
#       bool:   the "new" state of this state-machine.                        #
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       This state-machine has just two states, represented by the boolean    #
#       value of the `escape` variable. `escape` is `True` exactly when the   #
#       last consumed character was an unescaped escape character.            #
#                                                                             #
#       Consume a single character of line input, update the state and        #
#       output two characters (which may be empty) which will be parsed to    #
#       the next state-machine. The first character will either be the        #
#       input, if unescaped, or empty, if escaped. The next machine will      #
#       use this value to update its state. The second value will either be   #
#       the input, if it is not an unescaped escape character, or empty, it   #
#       it is. The next machine may use this value to generate its output.    #
#                                                                             #
###############################################################################
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


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _macro_state_machine(                                                 #
#               d, e, in_macro, transition, out_line, macro, params,          #
#               file_name="", line_no=0, pos=1, line=None)                    #
#                                                                             #
#   Parameters:                                                               #
#       d           -   string: zero or one characters which may be a         #
#                               control character indicating the beginning    #
#                               or end of a substitution parameter,           #
#                               required.                                     #
#                                                                             #
#       e           -   string: zero or one characters which might form       #
#                               part of the parsed output, required.          #
#                                                                             #
#       in_macro    -   bool:   part of the "current" state of this state-    #
#                               machine, True exactly when the context is     #
#                               inside a substitution parameter tag which     #
#                               has been completely opened and not            #
#                               completely closed, required.                  #
#                                                                             #
#       transition  -   bool:   part of the "current" state of this state-    #
#                               machine, True exactly when the first but      #
#                               not the second character of the opening or    #
#                               closing parameter tag sequence has been       #
#                               consumed in a context where the second        #
#                               character would change the value of           #
#                               `in_macro`, required.                         #
#                                                                             #
#       out_line    -   string: the parsed output line up to this point,      #
#                               this method will add its output to the        #
#                               given string if the current context is not    #
#                               `in_macro`, required.                         #
#                                                                             #
#       macro       -   string: the (iteratively constructed, partial) name   #
#                               of the current substitution parameter, this   #
#                               method will add its output to the given       #
#                               string when the current context is            #
#                               `in_macro`, required.                         #
#                                                                             #
#       params      -   dict:   the substitution parameters used for          #
#                               parsing the parametric file, required.        #
#                                                                             #
#       file_name   -   string: the name of the file, only used for error     #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#       line_no     -   int:    the line number from the file, only used      #
#                               for error messages so may safely be omitted   #
#                               if this is not required, default=0.           #
#                                                                             #
#       pos         -   int:    the position in the line, only used for       #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=1.              #
#                                                                             #
#       line        -   string: the line from the file, only used for error   #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#   Returns:                                                                  #
#       string: the updated value of `out_line`.                              #
#       string: the updated value of `macro`.                                 #
#       bool:   part of the "new" state of this state-machine, the updated    #
#               value of `in_macro`.                                          #
#       bool:   part of the "new" state of this state-machine, the updated    #
#               value of `transition`.                                        #
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       This state-machine four states, represented by a pair of boolean      #
#       value, the `in_macro` and `transition` variables. `in_macro` is       #
#       `True` exactly when the unescaped substring "<[" has been consumed    #
#       and the unescaped substring "]>" has not been since consumed.         #
#       `transition` is `True` exactly when `in_macro` is `False` and the     #
#       last character was an unescaped '<' or `in_macro` is `True` and the   #
#       last character was an unescaped ']'.                                  #
#                                                                             #
#       Consume the output of a single cycle of `_escape_state_machine()`,    #
#       update the state and update the parsed output and current parameter   #
#       name as appropriate. Which of these variables will be extended        #
#       depends upon the context however the `out_line` value will contain    #
#       the iteratively generated parsed output once this state-machine and   #
#       its predecessor have consumed the entire input line.                  #
#                                                                             #
###############################################################################
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


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       _get_parameter(                                                       #
#               params, param, file_name="", line_no=0, pos=1, line=None)     #
#                                                                             #
#   Parameters:                                                               #
#       params      -   dict:   the substitution parameters used for          #
#                               parsing the parametric file, required.        #
#                                                                             #
#       param       -   string: the name of the parameter to look up,         #
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
#       pos         -   int:    the position in the line, only used for       #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=1.              #
#                                                                             #
#       line        -   string: the line from the file, only used for error   #
#                               messages so may safely be omitted if this     #
#                               is not required, default="".                  #
#                                                                             #
#   Returns:    string: the value bound to the parameter or "" if no value    #
#                       is bound.
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       Check the parameter dictionary for the requested parameter, return    #
#       it if present, otherwise set it to "" and return this.                #
#                                                                             #
###############################################################################
def _get_parameter(params, param, file_name="", line_no=0, pos=1, line=None):
    if line == None:
        line = param
    
    try:
        return params[param]
    except KeyError:
        traceback.print_exception(
                        shared.ParameterError(
                                f"Missing parameter '{param}', (default='')",
                                (file_name, line_no, pos, line)))
        
        params[param] = ""
        
        return ""


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       parse_parameters(args)                                                #
#                                                                             #
#   Parameters:                                                               #
#       args    -   list:   a list of command line arguments which may, or    #
#                           may not include parameter value bindings,         #
#                           required.                                         #
#                                                                             #
#       file_name   -   string: the name of the file, only used for error     #
#                               messages so may safely be omitted if this     #
#                               is not required, default="argv".              #
#                                                                             #
#       line_no     -   int:    the line number from the file, only used      #
#                               error messages so may safely be omitted if    #
#                               this is not required, default=0.              #
#                                                                             #
#       line        -   string: the line from the file, only used for error   #
#                               messages so may safely be omitted if this     #
#                               is not required, default=None.                #
#                                                                             #
#   Returns:    dict:   the parameter dictionary mapping each parameter       #
#                       name to its bound value.                              #
#                                                                             #
#   Raises:                                                                   #
#       Normally nothing unless something is actually wrong with the call.    #
#                                                                             #
#   Description:                                                              #
#       Read key=value pairs from a list of command fields (or command line   #
#       arguments, warning of any arguments which don't contain exactly one   #
#       unescaped '=' and return a dictionary of these key, value pairs.      #
#       Note that if `file_name` or `line` are not provided, the default      #
#       behaviour is to assume that the source of arguments is the command    #
#       line `argv`. Error messages are formatted with this in mind.          #
#                                                                             #
###############################################################################
def parse_parameters(args, file_name="argv", line_no=0, line=None):
    params = {}
    
    for arg in args:
        escape = False
        
        idx = 0
        
        name_val = [""]
        
        for c in arg:
            if escape:
                name_val[idx] += c
                
                escape = False
            elif c == '\\':
                escape = True
            elif c == '=':
                idx += 1
                
                name_val += [""]
            else:
                name_val[idx] += c
        
        if idx == 1:
            params[name_val[0]] = name_val[1]
        else:
            if line == None:
                line = ' '.join(args)
            
            traceback.print_exception(
                            shared.ParameterError(
                                f"Bad parameter binding field \"{arg}\".",
                                (file_name, line_no, line.index(arg), line)))
    
    return params


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
