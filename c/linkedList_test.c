#include "linkedList.h"
#include <stdio.h>

#define DELIM                                                                  \
  if (word[0] == '#') {                                                        \
    printList(basePtr);                                                        \
    freeList(basePtr);                                                         \
    break;                                                                     \
  }

int main() {
  ListNode base = {(void *)NULL, (void *)NULL};
  const ListPtr basePtr = &base;

  ListPtr current = (ListPtr)basePtr;
  char word[100];
  while (scanf("%s", word) > 0) {
    DELIM
    current = addNode(current, word);
  }
  printf("\n");

  while (scanf("%s", word) > 0) {
    DELIM
    addNodeSorted(basePtr, word, 0);
  }
  printf("\n");

  while (scanf("%s", word) > 0) {
    DELIM
    addNodeSorted(basePtr, word, 1);
  }

  return 0;
}
