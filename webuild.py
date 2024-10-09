#! /usr/bin/python
###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `webuild.py`                                                 ####
####                                                                       ####
####    Summary: Command line tool for the `web-build` package.            ####
####                                                                       ####
####    Methods:                                                           ####
####        main(args)                                                     ####
####                -   Main execution method, not called on import.       ####
####                                                                       ####
####        open_files(args)                                               ####
####                -   Setup requested files for input and output.        ####
####                                                                       ####
###############################################################################
###############################################################################
import traceback
import sys

import webuildpkg


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       main(args)                                                            #
#                                                                             #
#   Parameters:                                                               #
#       args        -   list:   the argument list as passed at the command    #
#                               line (sys.argv). args[1] will specify the     #
#                               input file and args[2] will specify the       #
#                               output file, additional arguments may         #
#                               specify parameter bindings, required.         #
#                                                                             #
#   Returns:    int:    `EXIT_SUCCESS` or and error code.                     #
#                                                                             #
#   Raises:                                                                   #
#       Just about anything...                                                #
#                                                                             #
#   Description:                                                              #
#       The main execution method called if this module is executed rather    #
#       than imported. This method will resolve input and output file and     #
#       parse the contents of a parametric file to the output file.           #
#                                                                             #
###############################################################################
def main(args):
    infile, outfile = open_files(args[1:])
    
    file_type, line_no = webuildpkg.get_file_type(infile, outfile)
    
    if file_type == webuildpkg.TEMPLATE_ID:
        webuildpkg.template.parse_template(infile, outfile, line_no)
    elif file_type == webuildpkg.FRAGMENT_ID:
        webuildpkg.fragment.parse_fragment(infile, outfile, line_no)
    elif file_type == webuildpkg.PARAMETRIC_ID:
        params = webuildpkg.parametric.parse_parameters(args[3:])
        
        webuildpkg.parametric.parse_parametric(
                                            infile, outfile, params, line_no)
    else:
        traceback.print_exception(shared.ParseError(
                                    f"Invalid file declaration '{dec_line}', "
                                    f"assuming fragment file.",
                                    (file_name, line_no, 1, line.strip())))
        
        outfile.write(dec_line)
        
        webuildpkg.fragment.parse_fragment(infile, outfile, line_no)
    
    return 0


###############################################################################
#                                                                             #
#   Method:                                                                   #
#       open_files(args)                                                      #
#                                                                             #
#   Parameters:                                                               #
#       args        -   list:   the argument list as passed at the command    #
#                               line (sys.argv), ommiting the programme       #
#                               name. `args[0]` will specify the input file   #
#                               and args[1] will specify the output file.     #
#                                                                             #
#   Returns:    file, file: resolved input and output files, in that order.   #
#                                                                             #
#   Raises:                                                                   #
#       Hopefully nothing...                                                  #
#                                                                             #
#   Description:                                                              #
#       Open and return the input and output files (or return stdio           #
#       streams) based on command line arguments.                             #
#                                                                             #
###############################################################################
def open_files(args):
    infile  = sys.stdin
    outfile = sys.stdout
    
    try:
        infile  = webuildpkg.open_input( args[0])
        outfile = webuildpkg.open_output(args[1])
    except (IndexError, FileNotFoundError):
        pass
    
    return infile, outfile


###############################################################################
#                                                                             #
#   Non-function code to call `main()` when this file is executed rather      #
#   than imported.                                                            #
#                                                                             #
###############################################################################
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
