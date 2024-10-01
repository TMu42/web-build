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
    
    parse_parametric(infile, outfile, params={})
    
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


def parse_parametric(infile, outfile, params={}):
    line_no = 0
    
    if (line := infile.readline()) and line[0] == '#':
        line = infile.readline()
        
        line_no += 1
    
    line_no += 1
    
    try:
        command = shared.parse_command(
                    line, file_name=infile.name, line_no=line_no)[1:-1]
    except shared.ParseError as e:
        traceback.print_exception(e)
        
        outfile.write(line)
    else:
        if (not command[1:]) or command[1] != shared.PARAMETRIC_ID:
            traceback.print_exception(
                        shared.ParseError(
                            f"Invalid parametric file declaration.",
                            (infile.name, line_no, 1, line.strip())))
            
            outfile.write(line)
    
    while (line := infile.readline()):
        line_no += 1
        
        outfile.write(line)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
