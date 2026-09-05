%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *message);
%}

%token NUMBER

%left '+' '-'
%left '*' '/' '%'
%right UPLUS UMINUS

%%

input:
    expression '\n' { printf("Result: %d\n", $1); }
    ;

expression:
    NUMBER          { $$ = $1; }
    | '(' expression ')' { $$ = $2; }
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
    | '+' expression %prec UPLUS { $$ = $2; }
    | '-' expression %prec UMINUS { $$ = -$2; }
    ;

%%
