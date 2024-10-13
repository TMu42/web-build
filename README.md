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
                                                   │
            ┌────────────┬────────────┬────────────┼────────────┬────────────┬────────────┐
            │            │            │            │            │            │            │
        Blueprint    Blueprint     Template     Template    Parametric   Parametric    Fragment
                                                   │
            ┌────────────┬────────────┬────────────┼────────────┬────────────┬────────────┐
            │            │            │            │            │            │            │
         Template     Template    Parametric   Parametric    Fragment     Fragment    Plain Text
                                      │                                      │
            ┌────────────┬────────────┼────────────┐            ┌────────────┼────────────┐
            │            │            │            │            │            │            │
        Parameter    Parameter    Plain Text   Plain Text   Plain Text   Plain Text   Plain Text

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
characters. In the above example, the indent is: `"    "`. The indent may be an
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
command isn't otherwise needed. In the above example, the comment is:<br>
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
        Syntax:        :BLUEPRINT:[path/to/]blueprint;

        Function:      Import and parse the named blueprint file.

        Fields:        At least 2 fields.
                           Field_1    -    Must be exactly "BLUEPRINT".
                           Field_2    -    The name of the blueprint file to resolve and parse.
                           Field_3+   -    Unused.

        Details:       All paths are relative to the location of the containing file unless
                       otherwise specified. To resolve the file name, the directory  pointed to
                       by path/to/ will be serched for a file with the given name and then the
                       same name with the extensions ".blueprint" and ".blue" will be checked in
                       that order. The first matching file will be the resolved blueprint file -
                       even if it is not a blueprint file and a blueprint file exists at one of
                       the other locations. For this reason it is always safest to include the
                       file extension in the command field.
        
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

        Details:       All paths are relative to the location of the containing file unless
                       otherwise specified. To resolve the file name, the directory  pointed to
                       by path/to/ will be serched for a file with the given name and then the
                       same name with the extensions ".fragment" and ".frag" will be checked in
                       that order. The first matching file will be the resolved fragment file -
                       even if it is not a fragment file and a fragment file exists at one of
                       the other locations. For this reason it is always safest to include the
                       file extension in the command field.

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

        Details:       All paths are relative to the location of the containing file unless
                       otherwise specified. To resolve the file name, the directory  pointed to
                       by path/to/ will be serched for a file with the given name and then the
                       same name with the extensions ".parametric" and ".param" will be checked
                       in that order. The first matching file will be the resolved parametric
                       file - even if it is not a parametric file and a parametric file exists at
                       one of the other locations. For this reason it is always safest to include
                       the file extension in the command field.

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

        Details:       All paths are relative to the location of the containing file unless
                       otherwise specified. To resolve the file name, the directory  pointed to
                       by path/to/ will be serched for a file with the given name and then the
                       same name with the extensions ".template" and ".temp" will be checked in
                       that order. The first matching file will be the resolved template file -
                       even if it is not a template file and a template file exists at one of
                       the other locations. For this reason it is always safest to include the
                       file extension in the command field.

        Availability:  Blueprint, Template.

## Escape Character Syntax

Sometimes a file needs to include characters which would normally have special
meanings or effects, without invoking these effects. As such, web-build defines
a universal escape character `'\'`. Wherever this character is encountered in
a web-build file (except in a fragment file), it has the special effect of
negating any special effect of the next character (if any). The escape
character produces no output itself however if this character is needed in the
output, it can itself be escaped, i.e. `\\` -> `\`. This behaviour forms part
of the universal file syntax, available in the file text of any web-buid file
(except fragment files) but can also be used within commands with the same
effect. The escape character can be leveraged to include a `':'` or `';'` in a
command field or even to escape the special meaning of characters within a
field (such as `'='` in a `:PARAMETRIC;` command).

## Blueprint File Syntax

Blueprint files are the top level project files in the web-build hierachy.
They are used to describe and define the production of collections of files.
Unlike other file types, blueprints are not parsed to produce output directly,
rather they instruct the parser on which other files to parse and where to
write their output (if any). As such, blueprints are command driven files and
do not generally contain plain text. Any non-command lines (plain text) in a
blueprint have no semantic value, are ignored and may therefore be used as
comment space although this is not recommended as this behaviour may be
deprecated in future. You should always use `:;` for comments.

A blueprint file is declared with `::BLUEPRINT;` as the first line (or the
second line if the first line is shebang). Each non-empty line after this
should be a command, one of `:BLUEPRINT:name;`,
`:TEMPLATE:name[:output];`, `:FRAGMENT:name[:output];` or
`:PARAMETRIC:name[:output];`. If output is not provided, a default output
file will be selected.

It is recommended that blueprint files use the file extension ".blueprint" or
".blue" however this is not mandated. A consitant style for file extensions
should be used within a project.

As a general rule, blueprints should only invoke templates and other
blueprints. Invoking fragments and parametrics directly is discouraged as
these file types are not designed to produce whole output files. Nevertheless,
these files can be directly parsed to outputs and therefore may be included in
a blueprint file.

## Template File Syntax

Template files are second level project files in the web-build hierachy.
They are used to describe and define the production of individual files.
They may also be used to describe and define compound components of files.
Template files are parsed to produce a contiguous output which can be
written to a single file. They are hybrid command and file text driven.

A template file is declared with `::TEMPLATE;` as the first line (or the
second line if the first line is shebang). This means that an executable
(shebang) template to produce an executable (shebang) script could commence:

     #! /path/to/webuild
     ::TEMPLATE; to build executable script
     #! /path/to/script_interpreter
Each line after the declaration will be parsed as either file text or command.
File text will have escapes processed and then output as is whilst commands
will be executed and replaced by their output (if any). Commands should be one
of `:TEMPLATE:name;`, `:FRAGMENT:name;` or
`:PARAMETRIC:name[::param_1=val_1[:param_2=val_2[...]]];`.

It is recomended that template files use the file extension ".template" or
".temp" however this is not mandated. A consitant style for file extensions
should be used within a project.

## Fragment File Syntax

Fragment files are third level project files in the web-build hierachy.
They are used to describe and define basic and common components of files.
Fragment files are parsed to produce a contiguous output which can be
written to a single file but is usually not a complete file in itself. They
are entirely plain text driven.

A fragment file is declared with `::FRAGMENT;` as the first line (or the
second line if the first line is shebang). Each line after the declaration is
parsed verbatim to the output. Fragment files are the only web-build files
that have no special syntax, do not process commands and do not handle
escapes. Why you should choose to execute a fragment file with a shebang —
given that the output will merely be identity — is your business.
Nevertheless, this functionality has been provided for completeness.

It is recomended that fragment files use the file extension ".fragment" or
".frag" however this is not mandated. A consitant style for file extensions
should be used within a project.

## Parametric File Syntax

Parametric files are also third level project files in the web-build hierachy.
They are also used to describe and define basic and common components of files
however they are more flexible than fragment files and therefore require more
complex syntax. Parametric files are parsed to produce a contiguous output
which can be written to a single file but is usually not a complete file in
itself. They are mostly file text driven.

A parametric file is declared with `::PARAMETRIC;` as the first line (or the
second line if the first line is shebang). Each line after the declaration is
either a command or file text.

### Parametric file — commands

The only valid commands in parametric files are
parameter declarations which should be (but are not mandated to be) at the
head of the file. The behaviour of parameter declarations which occur after
the first instance of the parameter in the file is undefined. Parameter
declarations are of the following structure:
`::PARAM:PARAM_NAME[:[REQUIRED][:DEFAULT]]`. The parameter declaration
contains a number of standard components:
1. As with all declarations, Field_1 mush be empty.
2. Field_2 shall be exactly `PARAM` so the declaration begins `::PARAM`.
3. Field_3 specifies the parameter name. being declared. `PARAM_NAME` should
   exactly match the `PARAM_NAME` from the `<[PARAM_NAME]>` tokens in the file
   body.
4. Field_4 specifies whether the parameter is required at invocation.
   `REQUIRED` is either a boolean (True|False) or empty. This value may be
   implied (or even overwriten) by the next field.
5. Field_5 specifies the default value to bind to `PARAM_NAME` if not provided
   by the invocation. A non-empty value of `DEFAULT_VAL` may modify the
   `REQUIRED` value or interpretation, see below.

If neither `REQUIRED` nor `DEFAULT_VAL` are set, the declaration does not
change the default behaviour however the warning will be raised whether or not
the parameter occurs in the body of the parametric file. If only `REQUIRED` is
set, the template invocation will fail if the parameter is not bound. If only
`DEFAULT_VAL` is set, `REQUIRED` is set to `False`. If both `REQUIRED` and
`DEFAULT_VAL` are set and `REQUIRED` is `True`, it will raise only a warning
(not the usual error) if the invocation fails to bind `PARAM_NAME` and the
invocation will succeed (notwithstanding other errors).

### Parametric file — file text syntax

In addition to command syntax, parametric files also provide some file text
syntax. Escapes (`\`) are valid and processed throughout the file (commands
and file text) in the same way as for other file types (except fragment
files).

The other main file text syntax available in parametric files if the Parameter
Token. Parameter Tokens form the basis of why parametric files are more
powerful than fragment files. Parameter Tokens are the in-line macros which —
when parsed — are substituted for the values bound to each parameter.
Parameter Tokens are valid anywhere within file text (not in command lines) as
long as they do not span more than one line.

The syntax for Parameter Tokens is `<[PARAM_NAME]>` where
`PARAM_NAME` is the name of the parameter bound either by a declaration
command or at invocation in another file (using the `:PARAMETRIC` command). If
the literal string `"<["` needs to appear within the plain text portion of a
parametric file, either or both characters need to be escaped. The recommended
escape is `\<[` however `<\[` and `\<\[` are also valid. The same is true if
the literal string `"]>"` needs to appear within a Parameter Token (however
this is very bad style and highly discouraged, PLEASE don't use these
characters in parameter names).

Each named parameter may appear (as a Parameter Token) as many times as needed
within a file, or even on the same line. There is no limit to the number of
parameters which can be provided however, if the number of parameters set in
each invocation becomes unworkable, you should reconsider the design structure
of your project.

Example behaviour of parameter declarations when unbound at invocation:

`::PARAM:A;`            -> Bind `""` to `<[A]>` with unbound warning.

`::PARAM:B:True;`       -> Fail with unbound error.

`::PARAM:C:False;`      -> Silently bind `""` to `<[C]>`.

`::PARAM:D::foo;`       -> Silently bind `"foo"` to `<[D]>`.

`::PARAM:E:True:bar`    -> Bind `"bar"` to `<[E]>` with unbound warning.

`::PARAM:F:False:baz`   -> Silently bind `"baz"` to `<[F]>`.




