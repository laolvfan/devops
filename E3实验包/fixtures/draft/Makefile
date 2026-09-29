CC := cc
CFLAGS := -Wall -Wextra -O2

.PHONY: all clean

all: hello

hello: main.c
	$(CC) $(CFLAGS) main.c -o hello

clean:
	rm -f hello