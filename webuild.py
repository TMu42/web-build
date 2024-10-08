###############################################################################
###############################################################################
####                                                                       ####
####    Copyright: © 2024 TMu42, All Rights Reserved.                      ####
####                                                                       ####
####    File: `webuild.py`                                                 ####
####                                                                       ####
####    Summary: Command line tool for the `web-build` package.            ####
####                                                                       ####
###############################################################################
###############################################################################
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
    try:
        infile = open(args[1], 'r')
    except IndexError:
        infile  = sys.stdin
        outfile = sys.stdout
    else:
        try:
            outfile = webuildpkg.open_output(args[2])
        except IndexError:
            outfile = sys.stdout
    
    dec_line, line_no = webuildpkg.parse_shebang(infile)
    
    try:
        file_dec = webuildpkg.parse_command(dec_line, infile.name, line_no)
        
        file_type = file_dec[2]
    except webuild.ParseError:###################
    
    
    return 0


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
