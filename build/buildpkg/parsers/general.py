import sys

from . import shared
from . import template
from . import fragment
from . import parametric


ID_TEMPLATE   = "TEMPLATE"
ID_FRAGMENT   = "FRAGMENT"
ID_PARAMETRIC = "PARAMETRIC"


FILE_IDS = { ID_TEMPLATE   : template,
             ID_FRAGMENT   : fragment,
             ID_PARAMETRIC : parametric }


def parse_file(f, path="", ftype=None, params={}, outfile=sys.stdout):
    pass


def parse_file_from_command(command, path=""):
    if isinstance(command, str):
        command = shared.parse_command(line)[1:-1]
    
    if command[0] in FILE_IDS:
        f = FILE_IDS[command[0]].resolve_file(command[1], path=path)
        
        FILE_IDS[command[0]].parse_file
