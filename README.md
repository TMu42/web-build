# Build

## Usage

    build.py TEMPLATE_FILE [OUTPUT_FILE]

## Parameters

    TEMPLATE_FILE   -   the template from which to produce output file (see
                        syntax below).
    
    OUTPUT_FILE     -   the file to write output to.
    
## Template File Syntax

Any plaintext file could be a valid template file - as long as it commences
with the template file identifier - however without the following syntax, the
output will generally be identity.

A template file should commence with the line `::TEMPLATE;` with a comment
permitted following the semicolon. In order to comply with shebang syntax, if
the first line commences with a hash ('#'), it will be ignored and the second
line shall be `::TEMPLATE;`. This is a special case, all other `#` commencing
lines will be preserved in the output. This means that an executable (shebang)
template to produce an executable (shebang) script could commence as:

    `#! /path/to/build.py
     ::TEMPLATE; to build executable script
     #! /path/to/interpreter`

It is also recomended that template files use the file extension `.template`
however this is not mandated. A consitant style for file extensions should be
used within a project.

### General Template Syntax

The following syntax is available throughout the template file:

1. Any line commencing with the `\` character (preceeded only by whitespace)
   is treated as a literal line, the `\` is stripped however the whitespace
   (if any) is preserved.
   
        `    \:This is a line commencing with four spaces and a colon.`
        ->
        `    :This is a line commencing with four spaces and a colon.`
        
        `\\This is a line commencing with a back slash.`
        ->
        `\This is a line commencing with a backslash.`
        
        `\\:This is a line commencing with a back slash and a colon.`
        ->
        `\:This is a line commencing with a back slash and a colon.`

   Note that the `\` character is a general escape character throughout the
   `build.py` syntax and must be escaped (`\\`) wherever it is needed in an
   output. The character directly following a `\` will be output as literal,
   whether or not it has a special meaning.
   
2. Any line commencing with the `:` character (preceeded only by whitespace)
   is treated as a command. If an output line needs to commence with a `:`, it
   should be escaped with a `\`. Commands must reside on a single line and
   consume the entire line. Commands must be closed with the `;` character.
   Anything following the first `;` on a command line is ignored and this
   space should be used for comments. An empty command `:;` can be used to
   insert a comment where no command is issued. The whitespace indent
   preceeding a command is ignored and context indentation must be generated
   by the command or otherwise specified.
   
        `:;This line is just a comment, nothing will be echoed to the output.`
    
        `    :command;This line will be replaced by the output of "command".`

   Note, the template file writer/user is expected to ensure that all commands
   are valid.

3. Any line whose first (non-whitespace) character is not the `:` character
   will be echoed to the output after escapes have been processes.

### Template Command Syntax

Commands commence with a colon and are composed of a series of fields,
delimeted by further colons. The final field in a command must be terminated
with a semicolon. Neither the colon, nor the semicolon should occur unescaped
within a command other than as the delimeter and terminator. The general form
of commands is:

    `:FIELD_1[:FIELD_2[:FIELD_3[...]]; comment`

where any field may be empty.

The following command types are available in template files:

1. `::DECLARATION;`
            -   Declarations are special commands where field 1 is empty, i.e.
                they commence with two colons instead of just one. As the
                first line of a file, this declares the file type and must be
                `::TEMPLATE;` to declare a template file. Template files do
                not accept any other declarations.

2. `:FRAGMENT:[path/to/]fragment;`
            -   The :FRAGMENT command is specified with field 1 taking the
                exact value `FRAGMENT`. Field 2 shall be the path to a
                fragment file. All paths are relative to the read context of
                the template file. This line shall be substituted by the
                verbatim contents, excluding the declaration line and shebang
                (if present) of `[path/to/]fragment`. If this file is not
                present, build.py must try `[path/to/]fragment.fragment` and
                `[path/to/]fragment.frag` in that order. This command will
                fail if the file path cannot be resolved and may fail if the
                file is not declared as a `::FRAGMENT;`.

3. `:PARAMETRIC:[path/to/]parametric[:param1=value1[:param2=value2[...]]];`
            -   The :PARAMETRIC command is specified with field 1 taking the
                exact value `PARAMETRIC`. Field 2 shall be the path to a
                parametric file. File resolution is the same as for the
                fragment command except the extensions tried (in order) are:
                "", ".parametric" and ".param". This line shall be substituted
                by the parsed contents of the resolved file path. Any fields
                specified beyond field 2 will be parsed as param=value pairs.
                These fields must contain exactly one unescaped equals sign.
                This command will fail if the file path cannot be resolved and
                may fail if the file is not declared as a `::PARAMETRIC;` or
                if required parameters are not provided. Parametric files are
                similar to fragment files except that they may declare and
                resolve parameters when they are parsed.

### Fragment File Syntax

Fragment files are plaintext literal files. When parsed they will produce 
their literal content verbatim without any processing of tokens that may be
valid syntax in other file types. The only exceptions to this may occur in the
first two lines of the file. The first line of the file should be the fragment
file declaration `::FRAGMENT;[comment]` and will not be echoed to the output.
If the first line commences with the hash character, it will be assumed that
the first line is a shebang. In this case, the very next line should be the
file declaration and neither line shall be echoed. Why you should choose to
execute a fragment file with a shebang - given that the output will merely be
identity - is your business. Nevertheless, this functionality has been
provided.

Fragment file names should tend towards lower case styles but may contain any
valid file path characters. Remember that colon and semicolon will need to be
escaped where they are invoked. Recommended file extensions are ".fragment"
and ".frag" and these are mostly handled automatically where the file is
invoked, see :FRAGMENT command for details.

### Parametric File Syntax

All valid fragment files are valid parametric files (excepting the requisite
change of file declaration). Any lines which do not contain parametric syntax
will be parsed as verbatim plaintext. Much like fragment files, the first line
may be a shebang (which is ignored) and the first non-shebang line must be a
filetype declaration. These two lines (if present) will not produce output.
The following syntax is available in parametric files:

1. `<[PARAM_NAME]>`
        -   May occur anywhere in the file which is not a command or comment
            but must be contained on a single line in each instance. It will
            be substituted for the value bound to `PARAM_NAME` at invocation
            Each `PARAM_NAME` may appear any number of times in the file. The
            default behaviour (if not otherwise declared) is for parameters
            not mapped at invocation to raise a warning and default to an
            empty string substitution. To modify this behaviour, a declaration
            for the parameter is required. It is recomended that parameter
            names should be in allcaps style.

2. `::PARAM:PARAM_NAME[:[REQUIRED][:DEFAULT_VAL]];`
        -   This is the standard syntax for a parameter declaration. All
            parameter declarations should occur at the top of the file,
            immediately following the file declaration. The parameter
            declaration syntax contains a number of standard components:
                1. As with all declarations, field 1 mush be empty.
                2. Field 2 shall be exactly `PARAM` so the declaration begins
                   `::PARAM`.
                3. Field 3 specifies the parameter name. being declared.
                   `PARAM_NAME` should exactly match the `PARAM_NAME` from the
                   `<[PARAM_NAME]>` tokens in the file body.
                4. Field 4 specifies whether the parameter is required at
                   invocation. `REQUIRED` is either a boolean (True|False) or
                   empty. This value may be implied (or even overwriten) by
                   the next field.
                5. Field 5 specifies the default value to bind to `PARAM_NAME`
                   if not provided by the invocation. A non-empty value of
                   `DEFAULT_VAL` may modify the `REQUIRED` value or
                   interpretation, see below.
            If neither `REQUIRED` nor `DEFAULT_VAL` are set, the declaration
            does not change the default behaviour however the warning will be
            raised whether or not the parameter occurs in the body of the
            parametric file. If only `REQUIRED` is set, the template
            invocation will fail if the parameter is not bound. If only
            `DEFAULT_VAL` is set, `REQUIRED` is set to `False`. If both
            `REQUIRED` and `DEFAULT_VAL` are set and `REQUIRED` is `True`, it
            will raise only a warning (not the usual error) if the invocation
            fails to bind `PARAM_NAME` and the invocation will succeed
            (notwithstanding other errors). Example behaviour when unbound at
            invocation:
                `::PARAM:A;`            -> Bind `""` to `<[A]>` with unbound
                                           warning.
                `::PARAM:B:True;`       -> Fail with unbound error.
                `::PARAM:C:False;`      -> Silently bind `""` to `<[C]>`.
                `::PARAM:D::foo;`       -> Silently bind `"foo"` to `<[D]>`.
                `::PARAM:E:True:bar`    -> Bind `"bar"` to `<[E]>` with
                                           unbound warning.
                `::PARAM:F:False:baz`   -> Silently bind `"baz"` to `<[F]>`.

3. `\`  -   As with the template format, a line commencing with a backslash is
            treated as literal with the leading slash stripped. In this way, a
            literal line commencing with `:` or `\` can be achieved by
            pre-appending a backslash. In parametric files, the backslash can
            also be used to escape a single parameter token (or rather it can
            be used to escape the opening of a parameter token, e.g. `\<[A]>`
            will output the literal `<[A]>` without attempting to perform
            substitution. Note that `\` is a general escape character that
            must itself be escaped (`\\`) to achieve a literal `\` in the
            output.
            Examples:
                `::PARAM:X;`        ->  No output but parameter `X` declared.
                `\::PARAM:X;`       ->  `::PARAM:X;`.
                `\\::PARAM:X;`      ->  `\::PARAM:X;`.
                `\text`             ->  `text`.
                `\\text`            ->  `\text`.
                `text <[A]> text`   ->  `text VALUE_BOUND_TO_A text`.
                `\:text <[A]> text` ->  `:text VALUE_BOUND_TO_A text`.
                `\\text <[A]> text` ->  `\text VALUE_BOUND_TO_A text`.
                `text \<[A]> <[B]>` ->  `text <[A]> VALUE_BOUND_TO_B`.
                `text \\<[A]>`      ->  `text \VALUE_BOUND_TO_A`.
                `text \\\<[A]>`     ->  `text \<[A]>`.
                `text \<[<[A]>]>`   ->  `text <[VALUE_BOUND_TO_A]>`.
