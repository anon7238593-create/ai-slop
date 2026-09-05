CC ?= cc
CFLAGS ?= -Wall -Wextra -std=c99

expression: parser.c expression.c
	$(CC) $(CFLAGS) -o $@ parser.c expression.c

parser.c parser.h: expression.y
	yacc -d -o parser.c expression.y

clean:
	rm -f expression parser.c parser.h

.PHONY: clean
