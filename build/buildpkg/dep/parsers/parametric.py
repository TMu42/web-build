import tempfile
import sys
import re

from . import shared

from .. import errors


DEC_PARAM = "PARAM"

PARAM_NAME = re.compile(r"^[\w\.\-]+$")

BOOL_STR = { "True" : True, "False" : False }

R_KEY = 0
R_VAL = 1


def parse_line(line, outfile=sys.stdout, params={}, **kwargs):
    pass


def parametric_parser(pfile=None, fpath="", prefix=None, parse_file=None,
                                                        params="", **kwargs):
    params = _params_to_dict(params)
    
    parsed_files = []
    
    if prefix is not None:
        parsed_files.append(tempfile.TemporaryFile(mode='w+'))
        
        parsed_files[-1].write(prefix)
    
    if pfile is not None:
        parsed_files.append(tempfile.TemporaryFile(mode='w+'))
        
        newline = True
        command = False
        
        while (line := pfile.readline(CHUNK_SIZE)):
            newline, command, parsed_files = parse_parametric_line(
                                                    line, newline, command,
                                                    fpath, parsed_files,
                                                    params)
    
    return parsed_files


def parse_parametric_line(line, newline=True, comm=False, fpath="",
                          parsed_files=[tempfile.TemporaryFile(mode='w+')],
                          params={}):
    if newline and shared.COMMAND.match(line):
        cmd = shared.COMMAND.sub(r"\1", line).strip()
        
        comm = True
        
        if shared.COM_DECLARE.match(cmd):
            dec = cmd.strip().split(':')[1:]
            
            if dec[0] == DEC_PARAM:
                dec += (4 - len(dec))*[""]  # pad dec to length 4 with ""s
                
                try:
                    required = BOOL_STR[dec[2]]
                except KeyError:
                    required = None
                
                if dec[1] not in params:
                    if required:
                        if dec[3] == "":
                            errors.unbound_parameter_error(
                                f"Required parameter {dec[1]} not provided.")
                        else:
                            errors.unbound_parameter_error(
                                f"Required parameter with default value "
                                f"{dec[1]} not provided.", mode="WARNING")
                    elif required is None:
                        if dec[3] == "":
                            errors.unbound_parameter_error(
                                f"Parameter without default value {dec[1]} "
                                f"not provided.", mode="WARNING")
                    
                    params[dec[1]] = dec[3]
            else:
                errors.unrecognized_command_error(
                    f"Unrecognized declaration {dec[0]}", mode="WARNING")
                
                comm = False
        else:
            errors.unrecognized_command_error(
                f"Unrecognized command {cmd}", mode="WARNING")
            
            comm = False
        #elif newline:
        #    comm = False
        
        if not comm:
            rebuild = ""
            
            split_on_dbl_esc = line.split("\\\\")
            
            for tok in split_on_dbl_esc:
                split_on_esc = tok.split('\\')
                
                first = True
                
                for tik in split_on_esc:
                    if first:
                        first = False
                    else:
                        rebuild += tik[0]
                        
                        tik = tik[1:]
                    
                    


def _params_to_dict(params=""):
    param_dict = {}
    key_val    = ["", ""]
    read_to    = R_KEY
    esc        = False
    quot       = False
    
    for c in params:
        if esc or (not c in '"\\' and quot):
            key_val[read_to] += c
            
            esc = False
        elif c == '\\':
            esc = True
        elif c == '"':
            quot = not quot
        elif read_to == R_KEY and c == '=':
            read_to = R_VAL
        elif read_to == R_VAL and c == ',':
            param_dict[key_val[R_KEY]] = key_val[R_VAL]
            
            key_val = ["", ""]
            read_to = R_KEY
        else:
            key_val[read_to] += c
    
    param_dict[key_val[R_KEY]] = key_val[R_VAL]
    
    if quot:
        errors.syntax_error(f"Syntax error: quote mismatch in parameter "
                            f"string \"{params}\"")
    elif esc:
        errors.syntax_error(f"Syntax warning: escape character `\\` in final "
                            f"position has no effect in parameter string "
                            f"\"{params}\"")
    
    return param_dict;



##################### End of Code ############################################
#
#
#
##################### End of File ############################################
