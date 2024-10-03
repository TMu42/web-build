import sys


STDIOS = ['-', '']

FRAGMENT_ID   = "FRAGMENT"
PARAMETRIC_ID = "PARAMETRIC"


class ParseError(SyntaxError): pass
class ParameterError(SyntaxError): pass


def open_output(name):
    if name in STDIOS:
        return sys.stdout
    
    return open(name, 'w')


def parse_shebang(infile):
    if (line := infile.readline()) and line[0] == '#':
        return infile.readline(), 2
    
    return line, 1


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
