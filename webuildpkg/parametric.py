import traceback
import sys

try:
    from . import shared
except ImportError:
    import shared


PARAMETRIC_EXTS = ["", ".parametric", ".param"]


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
    
    return 0


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
        traceback.print_exception(shared.ParseError(
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
