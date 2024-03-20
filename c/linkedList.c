#include "linkedList.h"
#include "types.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// вставить элемент непосредственно после указанного элемента
// вернуть добавленный элемент
ListPtr addNode(ListPtr p, const char *word) {
  ListPtr np = (ListPtr)malloc(sizeof(ListNode));
  np->word = strcpy((char *)malloc(strlen(word) + 1), word);
  np->next = NULL;
  p->next = np;
  return np;
}

// вставить элемент после указанного элемента
// в позицию, соответствующую сортировке
// вернуть добавленный элемент
ListPtr addNodeSorted(ListPtr base, const char *word, char unique) {
  ListPtr cur = base;
  // ищем, куда вставлять новый элемент:
  // либо в конец списка
  // либо перед элементом, который больше вставляемого
  int cmpRes;
  while (cur->next != NULL && (cmpRes = strcmp(word, cur->next->word)) > 0) {
    cur = cur->next;
  }
  if (cur->next != NULL && unique == 1 && cmpRes == 0) {
    return cur->next;
  }
  ListPtr np = (ListPtr)malloc(sizeof(ListNode));
  np->word = strcpy((char *)malloc(strlen(word) + 1), word);

  // если вставляем в конец
  if (cur->next == NULL) {
    np->next = NULL;
    cur->next = np;
  } else {
    np->next = cur->next;
    cur->next = np;
  }
  return np;
}

void freeList(const ListPtr bp) {
  if (bp == NULL)
    return;
  ListPtr cur = bp->next;
  bp->next = NULL;
  ListPtr next;
  while (cur != NULL) {
    next = cur->next;
    cur->next = NULL;
    free(cur->word);
    free(cur);
    cur = next;
  }
}

void printList(const ListPtr bp) {
  if (bp == NULL)
    return;
  ListPtr cur = bp->next;
  while (cur != NULL) {
    printf("%s\n", cur->word);
    cur = cur->next;
  }
}

void dumpList(const ListPtr bp) {
  ListPtr cur = bp;
  while (cur != NULL) {
    printf("addr:%p word:%s next:%p\n", (void *)cur, cur->word,
           (void *)cur->next);
    cur = cur->next;
  }
}
