CC ?= cc
CFLAGS ?= -Wall -Wextra -std=c99

statement_parser: parser.c statement.c
	$(CC) $(CFLAGS) -o $@ parser.c statement.c

parser.c parser.h: statement.y
	yacc -d -o parser.c --defines=parser.h statement.y

clean:
	rm -f statement_parser parser.c parser.h y.tab.h

.PHONY: clean
