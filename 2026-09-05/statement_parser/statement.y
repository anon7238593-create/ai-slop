%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *message);
int get_variable(const char *name);
void set_variable(const char *name, int value);
%}

%union {
    int number;
    char *identifier;
}

%token <number> NUMBER
%token <identifier> IDENT
%token LET PRINT
%token EQ NE LE GE

%type <number> expression

%left EQ NE '<' '>' LE GE
%left '+' '-'
%left '*' '/' '%'
%right UPLUS UMINUS

%%

program:
    statements
    ;

statements:
    /* empty */
    | statements statement
    ;

statement:
    LET IDENT '=' expression ';'
        {
            set_variable($2, $4);
            free($2);
        }
    | PRINT expression ';'
        {
            printf("=> %d\n", $2);
        }
    | error ';'
        {
            yyerrok;
            fprintf(stderr, "Skipped invalid statement\n");
        }
    ;

expression:
    NUMBER                  { $$ = $1; }
    | IDENT                 { $$ = get_variable($1); free($1); }
    | '(' expression ')'    { $$ = $2; }
    | expression '+' expression { $$ = $1 + $3; }
    | expression '-' expression { $$ = $1 - $3; }
    | expression '*' expression { $$ = $1 * $3; }
    | expression '/' expression
        {
            if ($3 == 0) {
                yyerror("division by zero");
                YYERROR;
            }
            $$ = $1 / $3;
        }
    | expression '%' expression
        {
            if ($3 == 0) {
                yyerror("modulo by zero");
                YYERROR;
            }
            $$ = $1 % $3;
        }
    | expression '<' expression  { $$ = $1 < $3; }
    | expression '>' expression  { $$ = $1 > $3; }
    | expression LE expression   { $$ = $1 <= $3; }
    | expression GE expression   { $$ = $1 >= $3; }
    | expression EQ expression   { $$ = $1 == $3; }
    | expression NE expression   { $$ = $1 != $3; }
    | '+' expression %prec UPLUS  { $$ = $2; }
    | '-' expression %prec UMINUS { $$ = -$2; }
    ;

%%
