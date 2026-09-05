#include <stdio.h>

#include "parser.h"

int yyparse(void);
extern int yylval;

int yylex(void)
{
    int value;
    int character;

    do {
        character = getchar();
    } while (character == ' ' || character == '\t');

    if (character == EOF || character == '\n') {
        return character;
    }

    if (character >= '0' && character <= '9') {
        ungetc(character, stdin);
        if (scanf("%d", &value) != 1) {
            return 0;
        }
        yylval = value;
        return NUMBER;
    }

    return character;
}

void yyerror(const char *message)
{
    fprintf(stderr, "Parse error: %s\n", message);
}

int main(void)
{
    return yyparse();
}
