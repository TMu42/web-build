import traceback
import sys

from . import shared


STDIOS = ['-', '']

FRAGMENT_ID = "FRAGMENT"

FRAGMENT_EXTS = ["", ".fragment", ".frag"]


class ParseError(SyntaxError): pass


def main(args):
    try:
        infile = open_fragment(args[1])
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    parse_fragment(infile, outfile)
    
    return 0


def open_fragment(name):
    if name in STDIOS:
        return sys.stdin
    
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


def open_output(name):
    if name in STDIOS:
        return sys.stdout
    
    return open(name, 'w')


def parse_fragment(infile, outfile):
    line_no = 0
    
    if (line := infile.readline()) and line[0] == '#':
        line = infile.readline()
        
        line_no += 1
    
    line_no += 1
    
    try:
        command = parse_command(
                    line, file_name=infile.name, line_no=line_no)[1:-1]
    except ParseError as e:
        traceback.print_exception(e)
        
        outfile.write(line)
    else:
        if (not command[1:]) or command[1] != FRAGMENT_ID:
            traceback.print_exception(
                        ParseError(
                            f"Invalid fragment file declaration.",
                            (infile.name, line_no, 1, line.strip())))
            
            outfile.write(line)
    
    while (line := infile.readline()):
        line_no += 1
        
        outfile.write(line)


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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
