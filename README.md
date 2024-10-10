# Web Build (web-build) `webuild`

## Usage

    python webuild.py [INPUT_FILE [OUTPUT_FILE]]
OR:

    ./webuild.py [INPUT_FILE [OUTPUT_FILE]]
OR when installed:

    webuild [INPUT_FILE [OUTPUT_FILE]]

### Parameters

    INPUT_FILE    -   a blueprint, template, fragment or parametric file, the file from which to
                      produce one or more output files (see syntax below).
    
    OUTPUT_FILE   -   the file to write output to.

## File Types

### Overview

                                               Blueprint
                                                   |
            +------------+------------+------------+------------+------------+------------+
            |            |            |            |            |            |            |
        Blueprint     Blueprint    Template     Template     Parametric   Parametric   Fragment
                                                   |
            +------------+------------+------------+------------+------------+------------+
            |            |            |            |            |            |            |
        Template     Parametric   Parametric    Template     Fragment     Fragment    Plain Text
                         |                                                   |
            +------------+------------+------------+            +------------+------------+
            |            |            |            |            |            |            |
        Parameter    Parameter    Plain Text   Plain Text   Plain Text   Plain Text    Plain Text

Blueprints are overall project plans, they may contain references to any
other file type. Templates describe the structure of individual project files
and may contain references to any other file types except blueprints.
Parametrics and fragments are reusable components of files which are used
primarily by templates to construct larger files with common or recuring
elements. Fragments are constant elements whilst parametrics may contain
variables (parameters).

### Blueprint

A blueprint or project outline, listing one or more other files and defining
how they should be handled and where output should be written. Blueprints may
invoke other blueprints and define the outputs for templates, parametrics and
fragments. Blueprints are essentially build scripts which define all the
web-build operations needed to build a project (or part thereof) from small,
managable chunks.

### Template

A template for a single file, containing direct plain text to output and
invocations to substitute the parsed contents of other web-build files.
Templates may invoke and insert other templates as well as fragments and
parametrics. Templates are essentially outlines of particular files.

### Fragment

A reusable chunk of literal, plain text content. Fragments are used to
define small chunks of code which can be substituted verbatim into multiple
template files or at multiple points in the same template file (or both).
Fragments are essentially literal macros which can be invoked by other files.

### Parametric

A reusable chunk of content with parametric components. Parametrics are used
to define small chunks of code with variable components which can be
parametrically substituted into multiple template files or at multiple points
in the same template file (or both) with different values. Parametrics are
essentially parameterized macros which can be invoked by other files.

## Command Syntax

Each web-build file type contains a combination of file text and commands.
File text is further divided into plain text - parsed unaltered to output (if
any) - and file specific syntax. This section focuses on command syntax.

Commands are lines which instruct the interpreter to perform actions. Some
commands produce output whilst others change the state of the interpreter for
future parsing. All file types (except fragments) may contain commands however
the list of valid commands varies by file type and context.

### Anatomy of a command

Each command must be on a single line and must occupy the whole line. Every
line in a file must either be a single command OR file text. A line may not
contain a combination of command and file text. A line may not contain more
than one command. A line is a command if and only if its first non-whitespace
character is `:`. A valid command must also contain an unescaped `;` as a
terminator.

`    :THIS:IS:A:COMMAND; with an optional comment.`

A command has several components. The first component is the indent. This is
the substring preceeding the first `:` and must contain only whitespace
characters. In the above example, the indent is `"    "`. The indent may be an
empty string.

The next component is the body of the command. This contains all the semantic
value of the command. The body starts at the first `:` and ends at the first
unescaped `;`. In the above example, the body is `":THIS:IS:A:COMMAND;"`. The
body is divided into a series of 1 or more fields by unescaped `:`s. A field is
simply a string which may contain any characters except newline (currently
unsupported). `:`s and `;`s must be escaped so as not to terminate the field or
the command body. In the above example, the fields are: field_1 = `"THIS"`;
field_2 = `"IS"`; field_3 = `"A"`; field_4 = `"COMMAND"`. The first field is
also called the name of the command. There is no limit to the number of fields
a command body may contain however the command in question will determine how
many fields are required and optional. Unused fields may be truncated and may
produce warnings in some implementations.

The final component of any command is the comment. This is the substring which
follows the terminating `;`. The comment is universally ignored in all commands
and may be used to provide annotation to any file which is allowed to contain
commands. A special "empty" command `:;` may be used to add a comment where a
command isn't otherwise needed. In the above example, the comment is
`" with an optional comment."`.

### Command directory

    NOOP
        Syntax:        :;
        
        Function:      Guarenteed to do nothing, this simply provides space for a comment.

        Fields:        Exactly 1 field.
                           Field_1    -    Must be empty.

        Availability:  Blueprint, Template, Parametric.

    DECLARATION
        Syntax:        ::DECLARATION[:INFO[...]];

        Function:      Declare a property of the file being parsed.

        Fields:        At least 2 fields.
                           Field_1    -    Must be empty.
                           Field_2    -    The property being declared.
                           Field_3+   -    Any parameters applicable to the property.
        
        Availability:  Blueprint, Template, Parametric, Fragment (first line only).

        Examples:      The file type declaration is a DECLARATION command which must appear as
                       the first (non-shebang) line of any web-build file. File type
                       declarations are: ::BLUEPRINT;, ::TEMPLATE;, ::FRAGMENT and ::PARAMETRIC;.
                       ::PARAM:PARAM_NAME[:[REQUIRED][:DEFAULT]]; is another example of a
                       DECLARATION used in parametric files to declare the existance of a
                       parameter.

    BLUEPRINT
        Syntax:        :BLUEPRINT:NAME;

        Function:      Import and parse the named blueprint file.

        Fields:        At least 2 fields.
                           Field_1    -    Must be exactly "BLUEPRINT".
                           Field_2    -    The name of the blueprint file to resolve and parse.
                           Field_3+   -    Unused.

        Availability:  Blueprint.
        
    FRAGMENT
        Syntax:        :FRAGMENT:NAME[:OUTPUT];

        Function:      Import the named fragment file, parse it and substitute the output for
                       this line or output to the named output file.

        Fields:        At least 2 fields.
                           Field_1    -    Must be exactly "FRAGMENT".
                           Field_2    -    The name of the fragment file to resolve and parse.
                           Field_3    -    The fully resolved name of the output file
                                           (blueprint only).
                           Field_4+   -    Unused.

        Availability:  Blueprint, Template.

    PARAMETRIC
        Syntax:        :PARAMETRIC:NAME[:[OUTPUT][:PARAM_1=val_1[:PARAM_2=val_2[...]]]];

        Function:      Import the named parametric file, parse it with the given parameters and
                       substitute the output for this line or output to the named output file.

        Fields:        At least 2 fields.
                           Field_1    -    Must be exactly "PARAMETRIC".
                           Field_2    -    The name of the template file to resolve and parse.
                           Field_3    -    The fully resolved name of the output file
                                           (blueprint only).
                           Field_4+   -    The parameter=value pairs used to parse this
                                           instance of the parametric file.

        Availability:  Blueprint, Template.
    
    TEMPLATE
        Syntax:        :TEMPLATE:NAME[:OUTPUT];

        Function:      Import the named template file, parse it and substitute the output for
                       this line or output to the named output file.

        Fields:        At least 2 fields.
                           Field_1    -    Must be exactly "TEMPLATE".
                           Field_2    -    The name of the template file to resolve and parse.
                           Field_3    -    The fully resolved name of the output file
                                           (blueprint only).
                           Field_4+   -    Unused.

        Availability:  Blueprint, Template.

## Blueprint File Syntax

Blueprint files are the top level project files in the web-build hierachy.
Unlike other file types, blueprints are not parsed to produce output directly,
rather they instruct the parser on which other files to parse and where to
write their output (if any). As such, blueprints are command driven files and
do not generally contain plain text. Any non-command lines (plain text) in a
blueprint have no semantic value, are ignored and may therefore be used as
comment space although this is not recommended as this behaviour may be
deprecated in future. You should always use `:;` for comments.

A blueprint file is declared with `::BLUEPRINT;` as the first line (or the
second line if the first line is a shebang). Each non-empty line after this
should be a command, one of `:BLUEPRINT:name;`,
`:TEMPLATE:name[:output];`, `:FRAGMENT:name[:output];` or
`:PARAMETRIC:name[:output];`. If output is not provided, a default output
file will be selected.

## Template File Syntax

Any plaintext file could be a valid template file - as long as it commences
with the template file identifier - however without the following syntax, the
output will generally be identity (excluding the identifier and shebang if
present).

A template file should commence with the line `::TEMPLATE;[optional comment]`.
In order to comply with shebang syntax, if the first line commences with `#!`,
it will be ignored and the second line shall be `::TEMPLATE;`. This is a
special case, all other `#!` commencing lines will be preserved in the output.
This means that an executable (shebang) template to produce an executable
(shebang) script could commence as:

     #! /path/to/webuild
     ::TEMPLATE; to build executable script
     #! /path/to/script_interpreter

It is also recomended that template files use the file extension `.template`
or `.temp` however this is not mandated. A consitant style for file extensions
should be used within a project.

### General Template Syntax

The following syntax is available throughout the template file:

1. Any line commencing with the `\` character (preceeded only by whitespace)
   is treated as a literal line, the `\` is stripped however the whitespace
   (if any) is preserved.
   
   `    \:This is a line commencing with four spaces and a colon.`<br>
   --><br>
   `    :This is a line commencing with four spaces and a colon.`<br><br>
   
   `\\This is a line commencing with a back slash.`<br>
   --><br>
   `\This is a line commencing with a backslash.`<br><br>
   
   `\\:This is a line commencing with a back slash and a colon.`<br>
   --><br>
   `\:This is a line commencing with a back slash and a colon.`<br>

   Note that the `\` character is a general escape character throughout the
   `build.py` syntax and must be escaped (`\\`) wherever it is needed in an
   output. The character directly following a `\` will be output as literal,
   whether or not it has a special meaning. There are no currently supported
   escape sequences for special or non-printing characters.
   
3. Any line commencing with the `:` character (preceeded only by whitespace)
   is treated as a command. If an output line needs to commence with a `:`, it
   should be escaped with a `\`. Commands must reside on a single line and
   consume the entire line. Commands must be closed with the `;` character.
   Anything following the first `;` on a command line is ignored and this
   space should be used for comments. An empty command `:;` can be used to
   insert a comment where no command is issued. The whitespace indent
   preceeding a command is ignored and context indentation must be generated
   by the command or otherwise specified.
   
   `:;This line is just a comment, nothing will be echoed to the output.`
    
   `    :COMMAND;This line will be replaced by the output of "COMMAND".`

   Note, the template file writer/user is expected to ensure that all commands
   are valid.

4. Any line whose first (non-whitespace) character is not the `:` character
   will be echoed to the output after escapes have been processes.

### Template Command Syntax

Commands commence with a colon and are composed of a series of fields,
delimeted by further colons. The final field in a command must be terminated
with a semicolon. Neither the colon, nor the semicolon should occur unescaped
within a command other than as the delimeter and terminator. The general form
of commands is:

    :FIELD_1[:FIELD_2[:FIELD_3[...]];

where any field may be empty. The number of fields is not limited but will
depend upon the type of command being issued.

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
                if required parameters are not provided or if there are syntax
                errors in parsing parameter fields. Parametric files are
                similar to fragment files except that they may declare and
                resolve parameters when they are parsed.

4. `:TEMPLATE:[path/to]template;`
           -    The :TEMPLATE command is specified with field 1 taking the
                exact value `TEMPLATE`. Field 2 shall be the path to a
                template file. All paths are relative to the read context of
                the template file. This line shall be substituted by the
                recursively parsed contents of the sourced template file at
                `[path/to/]template`. If this file is not present, build.py
                must try `[path/to/]template.template` and
                `[path/to/]template.temp` in that order. This command will
                fail if the file path cannot be resolved and may fail if the
                file is not declared as a `::TEMPLATE;`.

### Fragment File Syntax

Fragment files are plaintext literal files. When parsed they will produce 
their literal content verbatim without any processing of tokens that may be
valid syntax in other file types. The only exceptions to this may occur in the
first two lines of the file. The first line of the file should be the fragment
file declaration `::FRAGMENT;[comment]` and will not be echoed to the output.
If the first line commences with `#!`, it will be assumed that the first line
is a shebang. In this case, the very next line should be the file declaration
and neither line shall be echoed. Why you should choose to execute a fragment
file with a shebang — given that the output will merely be identity — is your
business. Nevertheless, this functionality has been provided.

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

       -    May occur anywhere in the file which is not a command or comment but must be
            contained on a single line in each instance. It will be substituted for the value
            bound to `PARAM_NAME` at invocation. Each `PARAM_NAME` may appear any number of times
            in the file. The default behaviour (if not otherwise declared) is for parameters not
            mapped at invocation to raise a warning and default to an empty string substitution.
            To modify this behaviour, a declaration for the parameter is required. It is
            recomended that parameter names should be in allcaps style.

2. `::PARAM:PARAM_NAME[:[REQUIRED][:DEFAULT_VAL]];`

       -    This is the standard syntax for a parameter declaration. All parameter declarations
            should occur at the top of the file, immediately following the file declaration. The
            parameter declaration syntax contains a number of standard components:

                1. As with all declarations, field 1 mush be empty.
   
                2. Field 2 shall be exactly `PARAM` so the declaration begins `::PARAM`.
   
                3. Field 3 specifies the parameter name. being declared. `PARAM_NAME` should
                   exactly match the `PARAM_NAME` from the `<[PARAM_NAME]>` tokens in the file
                   body.
   
                4. Field 4 specifies whether the parameter is required at invocation. `REQUIRED`
                   is either a boolean (True|False) or empty. This value may be implied (or even
                   overwriten) by the next field.
   
                5. Field 5 specifies the default value to bind to `PARAM_NAME` if not provided by
                   the invocation. A non-empty value of `DEFAULT_VAL` may modify the `REQUIRED`
                   value or interpretation, see below.

            If neither `REQUIRED` nor `DEFAULT_VAL` are set, the declaration does not change the
            default behaviour however the warning will be raised whether or not the parameter
            occurs in the body of the parametric file. If only `REQUIRED` is set, the template
            invocation will fail if the parameter is not bound. If only `DEFAULT_VAL` is set,
            `REQUIRED` is set to `False`. If both `REQUIRED` and `DEFAULT_VAL` are set and
            `REQUIRED` is `True`, it will raise only a warning (not the usual error) if the
            invocation fails to bind `PARAM_NAME` and the invocation will succeed
            (notwithstanding other errors).

            Example behaviour when unbound at invocation:

                `::PARAM:A;`            -> Bind `""` to `<[A]>` with unbound warning.
   
                `::PARAM:B:True;`       -> Fail with unbound error.
   
                `::PARAM:C:False;`      -> Silently bind `""` to `<[C]>`.
   
                `::PARAM:D::foo;`       -> Silently bind `"foo"` to `<[D]>`.
   
                `::PARAM:E:True:bar`    -> Bind `"bar"` to `<[E]>` with unbound warning.
   
                `::PARAM:F:False:baz`   -> Silently bind `"baz"` to `<[F]>`.

3. `\`

       -    As with the template format, a line commencing with a backslash is treated as literal
            with the leading slash stripped. In this way, a literal line commencing with `:` or
            `\` can be achieved by pre-appending a backslash. In parametric files, the backslash
            can also be used to escape a single parameter token (or rather it can be used to
            escape the opening of a parameter token, e.g. `\<[A]>` will output the literal
            `<[A]>` without attempting to perform substitution. Note that `\` is a general escape
            character that must itself be escaped (`\\`) to achieve a literal `\` in the output.

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
