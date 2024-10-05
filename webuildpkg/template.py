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
except ImportError:
    import shared


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


def main(args):
    try:
        infile = open_template(args[1])#########################
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = shared.open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    parse_fragment(infile, outfile)
    
    infile.close()
    outfile.close()
    
    return 0


def open_fragment(name):
    if name in shared.STDIOS:
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


def parse_fragment(infile, outfile, line_no=0):
    if line_no == 0:
        line, line_no = shared.parse_shebang(infile)
        
        try:
            _assert_fragment(shared.parse_command(line, infile.name, line_no),
                             infile.name, line_no, line)
        except shared.ParseError as e:
            traceback.print_exception(e)
            
            outfile.write(line)
    
    while (line := infile.readline()):
        line_no += 1
        
        outfile.write(line)


def _assert_fragment(command, file_name="", line_no=0, line=""):
    cmd = command[1:-1]
    
    if (not cmd[1:]) or cmd[1] != shared.FRAGMENT_ID:
        raise shared.ParseError(f"Invalid fragment file declaration.",
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
