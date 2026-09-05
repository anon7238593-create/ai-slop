#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "parser.h"

#define MAX_VARIABLES 128

struct variable {
    char *name;
    int value;
};

static struct variable variables[MAX_VARIABLES];
static size_t variable_count;

static char *duplicate_string(const char *source)
{
    char *copy = malloc(strlen(source) + 1);

    if (copy == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    strcpy(copy, source);
    return copy;
}

static int find_variable(const char *name)
{
    size_t index;

    for (index = 0; index < variable_count; index++) {
        if (strcmp(variables[index].name, name) == 0) {
            return (int) index;
        }
    }

    return -1;
}

int get_variable(const char *name)
{
    int index = find_variable(name);

    if (index < 0) {
        fprintf(stderr, "Undefined variable: %s\n", name);
        return 0;
    }

    return variables[index].value;
}

void set_variable(const char *name, int value)
{
    int index = find_variable(name);

    if (index >= 0) {
        variables[index].value = value;
        return;
    }

    if (variable_count == MAX_VARIABLES) {
        fprintf(stderr, "Too many variables\n");
        return;
    }

    variables[variable_count].name = duplicate_string(name);
    variables[variable_count].value = value;
    variable_count++;
}

int yylex(void)
{
    char buffer[128];
    int character;
    size_t length;

    do {
        character = getchar();
    } while (isspace((unsigned char) character));

    if (character == EOF) {
        return 0;
    }

    if (isdigit((unsigned char) character)) {
        ungetc(character, stdin);
        if (scanf("%d", &yylval.number) != 1) {
            return 0;
        }
        return NUMBER;
    }

    if (isalpha((unsigned char) character) || character == '_') {
        length = 0;
        do {
            if (length + 1 < sizeof(buffer)) {
                buffer[length++] = (char) character;
            }
            character = getchar();
        } while (isalnum((unsigned char) character) || character == '_');
        buffer[length] = '\0';
        ungetc(character, stdin);

        if (strcmp(buffer, "let") == 0) {
            return LET;
        }
        if (strcmp(buffer, "print") == 0) {
            return PRINT;
        }

        yylval.identifier = duplicate_string(buffer);
        return IDENT;
    }

    if (character == '=' || character == '!' ||
        character == '<' || character == '>') {
        int next = getchar();

        if (character == '=' && next == '=') {
            return EQ;
        }
        if (character == '!' && next == '=') {
            return NE;
        }
        if (character == '<' && next == '=') {
            return LE;
        }
        if (character == '>' && next == '=') {
            return GE;
        }
        ungetc(next, stdin);
    }

    return character;
}

void yyerror(const char *message)
{
    fprintf(stderr, "Parse error: %s\n", message);
}

int main(void)
{
    int status = yyparse();
    size_t index;

    for (index = 0; index < variable_count; index++) {
        free(variables[index].name);
    }

    return status;
}
