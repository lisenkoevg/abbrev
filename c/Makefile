objects = extractAbbr 
tests = linkedList_test

warn = $(shell grep -v \# warn_config | tr \\n ' ')
excludeWarn = -Wsuggest-attribute=noreturn -Wsuggest-attribute=const -Wstrict-prototypes
override CFLAGS += -g -Wextra -Wall -Wpedantic -Werror $(filter-out $(excludeWarn), $(warn)) 
all: $(objects) $(tests)

extractAbbr linkedList_test: linkedList.c

%: %.c
	$(CC) $(CFLAGS) $^ -o $@

clean:
	@for f in $(addsuffix *, $(objects) $(tests)); do \
      file $$f | grep -qP "ELF|PE.*executable" && rm $$f; \
      true; \
	done

test:
	./runtests.sh
