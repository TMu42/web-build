import sys
import re

from .. import errors


SHEBANG = re.compile(r"^\#\!")                # #!...
COMMAND = re.compile(r"^\s*:([^;]*);(.*)$")   # :command; comment
ESCAPE  = re.compile(r"^(\s*)\\(.*)$")        # \literal
EQUALS  = re.compile(r"([^\\])=")

COMMAND_DECLARATION = ""
COMMAND_FRAGMENT    = "FRAGMENT"
COMMAND_PARAMETRIC  = "PARAMETRIC"

COMMANDS = [ COMMAND_DECLARATION, COMMAND_FRAGMENT, COMMAND_PARAMETRIC ]

#COM_FRAGMENT   = re.compile(r"^[\w\.\-\/]+$")   #A-Z,a-z,0-9,'.','-','/'
#COM_PARAMETRIC = re.compile(r"^([\w\.\-\/]+)\((.*)\)$")
#COM_DECLARE    = re.compile(r"^:")

K = 1024
M = K*K
G = K*M

CHUNK_SIZE = 32*K

ID_TEMPLATE   = "TEMPLATE"
ID_FRAGMENT   = "FRAGMENT"
ID_PARAMETRIC = "PARAMETRIC"

FILE_IDS = [ ID_TEMPLATE, ID_FRAGMENT, ID_PARAMETRIC ]


# Return a command line as a list of command tokens: idx 0 is the indent,
# idx -1 is the comment, everything in between is the actual command syntax.
def parse_command(line):
    esc = False
    comment = False
    opened = False
    command = [""]
    
    for c in line:
        if esc:
            command[-1] += c
            esc = False
        elif comment:
            command[-1] += c
        elif c == '\\':
            esc = True
        elif c == ':':
            command += [""]
            opened   = True
        elif c == ';':
            command += [""]
            comment  = True
        else:
            command[-1] += c
    
    if not opened or not comment or command[0].strip() != "":
        raise ValueError(f"{line.strip()} is not a valid command.")
    
    return command


def do_command(command, **kwargs):
    if len(command) > 0:
        if command[0] in COMMANDS:
            DO_COMMAND[command[0]](command[1:], **kwargs)
        else:
            errors.syntax_error(f"Unrecognized command: {command[0]}")

def _do_declaration(command, **kwargs):
    pass

def _do_fragment(command, fpath = "./", outfile=sys.stdout,
                                        parser=None, **kwargs):
    parser(fpath + command[0], ftype=ID_FRAGMENT, outfile=outfile)

def _do_parametric(command, **kwargs):
    params = {}
    
    for arg in command[1:]:
        eq_split = EQUALS.split(arg)
        
        if len(eq_split) == 3:
            params[eq_split[0] + eq_split[1]] = eq_split[2]
    
    parser(fpath + command[0], ftype=ID_PARAMETRIC,
                               params=params, outfile=outfile)

DO_COMMAND = { COMMAND_DECLARATION : _do_declaration,
               COMMAND_FRAGMENT    : _do_fragment,
               COMMAND_PARAMETRIC  : _do_parametric }


# Remove one layer of escape characters from a line of text (string)
def de_esc(line):
    de_esc_line = ""
    
    esc = False
    
    for c in line:
        if esc:
            de_esc_line += c
            
            esc = False
        elif c == '\\':
            esc = True
        else:
            de_esc_line += c

    if esc:
        errors.syntax_error(
            f"Line '{line}' ends in escape character", mode="WARNING")
    
    return de_esc_line


##################### End of Code ############################################
#
#
#
##################### End of File ############################################
