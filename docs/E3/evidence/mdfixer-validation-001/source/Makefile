CC = gcc
CFLAGS = -Wall -Wextra -O0

.PHONY: all clean
all: app

app: main.o
	$(CC) $(CFLAGS) -o $@ $^

main.o: main.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f app main.o