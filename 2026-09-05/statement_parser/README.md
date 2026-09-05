# Statement Parser

This example parses and executes a tiny statement-based language. Unlike the
expression parser in `yacc_test`, it does not reduce one input line to one
number. It parses a sequence of statements, stores named variables, evaluates
expressions using the stored state, and prints selected results.

The language supports:

- Assignment: `let name = expression;`
- Output: `print expression;`
- Integer arithmetic: `+`, `-`, `*`, `/`, and `%`
- Comparisons: `<`, `>`, `<=`, `>=`, `==`, and `!=`
- Parentheses and unary `+` and `-`
- Multiple statements in one input stream
- Recovery from a malformed statement at the next semicolon

Example input:

```text
let width = 4;
let height = 3;
let area = width * height;
print area;
print area == 12;
print area > 10;
```

Output:

```text
=> 12
=> 1
=> 1
```

The parser executes actions as soon as complete statements are recognized.
That stateful behavior is why this is more than a parser for a single
deducible expression.

## Files

### `statement.y`

This is the Yacc grammar.

```c
%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *message);
int get_variable(const char *name);
void set_variable(const char *name, int value);
%}
```

- `%{` and `%}` surround C declarations copied into the generated parser.
- The standard headers provide declarations used by grammar actions.
- `yylex` is the lexer supplied by `statement.c`.
- `yyerror` is called when the input does not match the grammar.
- `get_variable` and `set_variable` connect grammar actions to the symbol table
  implemented in `statement.c`.

```c
%union {
    int number;
    char *identifier;
}
```

- `%union` defines the possible semantic-value types carried by tokens and
  grammar rules.
- `number` stores integer values.
- `identifier` stores heap-allocated variable names.

```c
%token <number> NUMBER
%token <identifier> IDENT
%token LET PRINT
%token EQ NE LE GE
```

- `NUMBER` carries an integer in the `number` member.
- `IDENT` carries a variable name in the `identifier` member.
- `LET` and `PRINT` are keyword tokens without semantic values.
- `EQ`, `NE`, `LE`, and `GE` represent the multi-character comparison
  operators `==`, `!=`, `<=`, and `>=`.
- Single-character operators such as `+` and `(` are returned directly by the
  lexer and are written as literal characters in the grammar.

```c
%type <number> expression
```

- Declares that every `expression` rule produces an integer.

```c
%left EQ NE '<' '>' LE GE
%left '+' '-'
%left '*' '/' '%'
%right UPLUS UMINUS
```

- These declarations resolve ambiguous expression parses.
- Comparisons have the lowest precedence and return `0` or `1`.
- Addition and subtraction bind more tightly than comparisons.
- Multiplication, division, and modulo bind more tightly than addition.
- The artificial `UPLUS` and `UMINUS` symbols give unary signs the highest
  precedence.

```c
%%

program:
    statements
    ;

statements:
    /* empty */
    | statements statement
    ;
```

- The first `%%` starts the grammar rules.
- `program` is the start rule and accepts the complete statement sequence.
- `statements` may be empty, or it may append another statement recursively.
- The empty alternative lets an empty input file parse successfully.

```c
statement:
    LET IDENT '=' expression ';'
        {
            set_variable($2, $4);
            free($2);
        }
```

- Matches an assignment such as `let total = price * quantity;`.
- `$2` is the identifier name and `$4` is the calculated value.
- The action stores the value in the symbol table.
- The identifier was allocated by the lexer, so the action releases it after
  the name has been used.

```c
    | PRINT expression ';'
        {
            printf("=> %d\n", $2);
        }
```

- Matches a print statement.
- `$2` is evaluated before the action runs.
- The action writes the result.

```c
    | error ';'
        {
            yyerrok;
            fprintf(stderr, "Skipped invalid statement\n");
        }
    ;
```

- `error` is Yacc's built-in recovery token.
- If a statement is malformed, the parser discards input until the next
  semicolon.
- `yyerrok` tells Yacc that recovery is complete, allowing parsing to resume.

```c
expression:
    NUMBER                  { $$ = $1; }
    | IDENT                 { $$ = get_variable($1); free($1); }
    | '(' expression ')'    { $$ = $2; }
```

- A number evaluates to itself.
- An identifier evaluates through the symbol table, then its allocated name is
  freed.
- Parentheses preserve the value of the nested expression.
- An undefined variable produces an error and evaluates as `0` in this small
  example.

```c
    | expression '+' expression { $$ = $1 + $3; }
    | expression '-' expression { $$ = $1 - $3; }
    | expression '*' expression { $$ = $1 * $3; }
```

- These productions evaluate the three basic binary arithmetic operations.
- `$1` is the left operand, `$3` is the right operand, and `$$` is the result.

```c
    | expression '/' expression
        {
            if ($3 == 0) {
                yyerror("division by zero");
                YYERROR;
            }
            $$ = $1 / $3;
        }
```

- Performs integer division.
- The explicit check prevents undefined C behavior.
- `YYERROR` abandons the current parse reduction and enters Yacc recovery.

```c
    | expression '%' expression
        {
            if ($3 == 0) {
                yyerror("modulo by zero");
                YYERROR;
            }
            $$ = $1 % $3;
        }
```

- Performs integer remainder with the same zero-denominator protection.

```c
    | expression '<' expression  { $$ = $1 < $3; }
    | expression '>' expression  { $$ = $1 > $3; }
    | expression LE expression   { $$ = $1 <= $3; }
    | expression GE expression   { $$ = $1 >= $3; }
    | expression EQ expression   { $$ = $1 == $3; }
    | expression NE expression   { $$ = $1 != $3; }
```

- These productions implement the six comparisons.
- C comparison operators produce `0` for false and `1` for true, which makes
  their results printable and usable in later arithmetic.

```c
    | '+' expression %prec UPLUS  { $$ = $2; }
    | '-' expression %prec UMINUS { $$ = -$2; }
    ;

%%
```

- These rules implement unary plus and unary minus.
- `%prec` assigns each rule the precedence of its artificial marker.
- The final `;` ends the `expression` rules.
- The second `%%` ends the grammar section.

### `statement.c`

This file supplies the runtime support expected by the grammar.

```c
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "parser.h"
```

- The standard headers provide character classification, I/O, allocation, and
  string functions.
- `parser.h` is generated by Yacc and contains token constants plus the
  semantic-value declaration.

```c
#define MAX_VARIABLES 128

struct variable {
    char *name;
    int value;
};

static struct variable variables[MAX_VARIABLES];
static size_t variable_count;
```

- The symbol table is limited to 128 variables.
- Each entry owns a variable name and stores its integer value.
- `static` keeps the table private to this translation unit.

`duplicate_string` allocates a copy of an identifier. The lexer cannot point
into a reusable input buffer because each later token would overwrite it.
`find_variable` searches the table by name.

`get_variable` looks up a name, reports undefined variables, and returns its
value. `set_variable` updates an existing entry or appends a new one. It
duplicates the name so the table owns its storage.

```c
int yylex(void)
```

- This is the lexer entry point called by the generated parser.
- It skips whitespace, recognizes integers, recognizes identifiers and
  keywords, and returns punctuation or comparison tokens.

For numbers, the lexer puts the first digit back with `ungetc`, lets `scanf`
read the complete integer into `yylval.number`, and returns `NUMBER`.

For names, it reads letters, digits, and underscores into a bounded buffer.
The words `let` and `print` become keyword tokens; every other name becomes an
`IDENT` token with a heap-allocated `yylval.identifier`.

For `==`, `!=`, `<=`, and `>=`, it reads one-character lookahead and returns
the corresponding named token. A non-matching lookahead is put back so that it
is not lost.

`yyerror` prints syntax and semantic error messages. `main` starts `yyparse`,
then frees every variable name owned by the symbol table before returning the
parser status.

### `Makefile`

```make
CC ?= cc
CFLAGS ?= -Wall -Wextra -std=c99
```

- Selects the C compiler and warning flags while allowing command-line
  overrides.

```make
statement_parser: parser.c statement.c
	$(CC) $(CFLAGS) -o $@ parser.c statement.c
```

- Builds the executable from the generated parser and hand-written runtime.

```make
parser.c parser.h: statement.y
	yacc -d -o parser.c --defines=parser.h statement.y
```

- Generates the parser source and token header from the grammar.
- Explicit output names avoid relying on implementation-specific `y.tab.*`
  names.

```make
clean:
	rm -f statement_parser parser.c parser.h y.tab.h

.PHONY: clean
```

- Removes generated files and the executable.
- `.PHONY` ensures `clean` always runs as a command.

## Build and run

From this directory:

```sh
make
printf 'let width = 4;\nlet height = 3;\nlet area = width * height;\nprint area;\nprint area == 12;\n' | ./statement_parser
make clean
```

Expected output:

```text
=> 12
=> 1
```

Generated parser files and the executable are ignored by Git.
