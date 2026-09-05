%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *message);
%}

%token NUMBER

%%

input:
    expression '\n' { printf("Result: %d\n", $1); }
    ;

expression:
    NUMBER          { $$ = $1; }
    | expression '+' NUMBER { $$ = $1 + $3; }
    | expression '-' NUMBER { $$ = $1 - $3; }
    ;

%%
