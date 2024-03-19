#include <assert.h>
#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LETTERS_COUNT 33
#define ALL_LETTERS_COUNT (LETTERS_COUNT + LETTERS_COUNT)
#define MAX_WORD_LENGTH 100

#define PATH_DELIMITER_WIN '\\'
#define PATH_DELIMITER_LINUX '/'

typedef unsigned int uint;
typedef unsigned char uchar;

uchar lowerLetters[LETTERS_COUNT];
uchar upperLetters[LETTERS_COUNT];
uchar allLetters[ALL_LETTERS_COUNT];

void init(char *prog);
void readArrayFromFile(const char *filename, uchar *arr, uint length);
void concatArrays(uchar *dest, const uchar *src1, const uchar *src2,
                  uint srcLength);
void printArray(uchar *arr, uchar length);
uchar inArray(uchar c, const uchar *arr, uint length) __attribute__((const));
uchar isAbbrev(uint length, uint upperLettersCount) __attribute__((const));

// replaceBasename(buf, '<path>\basename', 'newname') =>
// return buf = <path>\newname
char *replaceBasename(char *buf, const char *path, const char *basename);

int main(int argc, char **argv) {
  init(argv[0]);

  uint count = 0;
  if (argc > 1)
    count = (uint)atoi(argv[1]);

  uchar currentWordLength = 0;
  uchar upperLetterCounter = 0;
  uint i = 0;
  int chInt;
  uchar ch;
  uchar currentWord[MAX_WORD_LENGTH];
  while ((chInt = getchar()) != EOF) {
    ch = (uchar)chInt;
    if (inArray(ch, allLetters, ALL_LETTERS_COUNT)) {
      currentWord[currentWordLength++] = ch;
      if (inArray(ch, upperLetters, LETTERS_COUNT))
        upperLetterCounter++;
    } else {
      if (currentWordLength == 0)
        continue;
      currentWord[currentWordLength] = '\0';
      if (currentWordLength > 1 &&
          isAbbrev(currentWordLength, upperLetterCounter)) {
        printf("%s\n", currentWord);
      }
      currentWordLength = upperLetterCounter = 0;
    }
    i++;
    if (count > 0 && i == count)
      break;
  }
  fprintf(stderr, "Total letters: %u\n", i);
  return 0;
}

void init(char *prog) {
  char buf[500];

  replaceBasename(buf, prog, "lowerLetters");
  readArrayFromFile(buf, lowerLetters, LETTERS_COUNT);

  replaceBasename(buf, prog, "upperLetters");
  readArrayFromFile(buf, upperLetters, LETTERS_COUNT);

  concatArrays(allLetters, upperLetters, lowerLetters, LETTERS_COUNT);
}

void readArrayFromFile(const char *filename, uchar *arr, uint length) {

  FILE *fd = fopen(filename, "r");
  if (fd == NULL) {
    fprintf(stderr, "error opening file '%s'\n", filename);
    abort();
  } else {
//     printf("Opening file '%s': success\n", filename);
  }
  uchar i = 0;
  uchar ch;
  while (fscanf(fd, "%hhX", &ch) > 0) {
    arr[i++] = ch;
  }
  assert(i == length);
  fclose(fd);
}

void concatArrays(uchar *dest, const uchar *src1, const uchar *src2,
                  uint srcLength) {
  for (uchar i = 0; i < srcLength; i++) {
    dest[i] = src1[i];
    dest[i + srcLength] = src2[i];
  }
}

void printArray(uchar *arr, uchar length) {
  for (uchar i = 0; i < length; i++)
    printf("%X ", arr[i]);
  printf("\n");
}

uchar inArray(uchar c, const uchar *arr, uint length) {
  for (uchar i = 0; i < length; i++) {
    if (arr[i] == c)
      return 1;
  }
  return 0;
}

uchar isAbbrev(uint length, uint upperLettersCount) {
  if (length <= 4)
    return upperLettersCount == length;
  else
    return upperLettersCount >= (length - 2);
}

char *replaceBasename(char *buf, const char *path, const char *basename) {
  uint progLength = (uint)(strlen(path));
  uint namePos = progLength - 1;
  while (path[namePos] != PATH_DELIMITER_WIN &&
         path[namePos] != PATH_DELIMITER_LINUX && namePos-- > 0)
    ;
  strcpy(buf, path);
  buf[namePos + 1] = '\0';
  strcat(buf, basename);
  return buf;
}
