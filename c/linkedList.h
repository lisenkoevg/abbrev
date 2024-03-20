typedef struct tnode *ListPtr;
typedef struct tnode {
  char *word;
  ListPtr next;
} ListNode;

ListPtr addNode(ListPtr p, const char * word);
void dumpList(const ListPtr bp);
void freeList(const ListPtr bp);
void printList(const ListPtr bp);
ListPtr addNodeSorted(ListPtr bp, const char * word, char unique);
