CC ?= cc
CFLAGS ?= -Wall -Wextra -std=c99

expression: y.tab.c expression.c
	$(CC) $(CFLAGS) -o $@ y.tab.c expression.c

y.tab.c y.tab.h: expression.y
	yacc -d expression.y

clean:
	rm -f expression y.tab.c y.tab.h

.PHONY: clean
