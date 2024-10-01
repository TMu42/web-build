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

K = 1024
M = K*K
G = K*M

CHUNK_SIZE = 32*K

#ID_TEMPLATE   = "TEMPLATE"
#ID_FRAGMENT   = "FRAGMENT"
#ID_PARAMETRIC = "PARAMETRIC"

#FILE_IDS = [ ID_TEMPLATE, ID_FRAGMENT, ID_PARAMETRIC ]


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
