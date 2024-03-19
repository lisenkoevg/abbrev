object = extractAbbr

warn = $(shell grep -v \# warn_config | tr \\n ' ')
excludeWarn = -Wsuggest-attribute=noreturn
override CFLAGS += -s -O3 -Wextra -Wall -Wpedantic -Werror $(filter-out $(excludeWarn), $(warn))

all: $(object)

%: %.c
	@$(CC) $(CFLAGS) $^ -o $@

clean:
	@rm -f *.exe

