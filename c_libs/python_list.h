#ifndef PYTHON_LISTS
#define PYTHON_LISTS
#include <stdio.h>
#include "python_string.h"
enum python_type {
    p_int,
    p_bool,
    p_list,
    p_string
};

struct Node {
    void* data;
    struct Node *next;
    enum python_type node_type;
};

struct List {
    int length;
    struct Node *head;
};

struct List * new_list();
void insert(struct List * head, struct Node * node);
void pushInt(struct List* head, int val);
void pushShort(struct List* head, short val);
void pushList(struct List* head, struct List * val);
void pushString(struct List* head, String * val);

String * getStringFromList(struct List* from, int pos);
String * getStringFromString(String* from, int pos);
struct Node* getNode(struct List* from, int pos);
int getInt(struct List* from, int pos);
short getShort(struct List* from, int pos);
struct List* getList(struct List* from, int pos);

struct List* concat_lists(struct List* list1, struct List* list2);
#define push(a, b) _Generic(b, int: pushInt, short: pushShort, struct List *: pushList, String*: pushString)(a, b)
#define getString(a, b) _Generic(a, struct List *: getStringFromList, String* : getStringFromString)(a, b)
#endif