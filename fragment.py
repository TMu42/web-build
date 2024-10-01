import tempfile
import sys


def main(args):
    try:
        infile = _open_fragment(args[1])
    except IndexError:
        infile  = tempfile.TemporaryFile('w+')
        
        while (line := sys.stdin.readline()):
            infile.write(line)
        
        infile.seek(0)
        
        outfile = sys.stdout
    else:
        try:
            outfile = open(args[2], 'w')
        except IndexError:
            outfile = sys.stdout
    
    while (line := infile.readline()):
        outfile.write(line)
    
    return 0


def _open_fragment(name):
    for file_name in [name, name + ".fragment", name + ".frag"]:
        try:
            f = open(file_name, 'r')
        except FileNotFoundError:
            pass
        else:
            return f
    
    return None


if __name__ == "__main__":
    sys.exit(main(sys.argv))
