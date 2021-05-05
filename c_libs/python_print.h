#include <stdio.h>
#include "python_list.h"
#include "python_string.h"

#ifndef PYTHON_PRINT
#define PYTHON_PRINT

void printInt(int x);

void printShort(short s);

void printList(struct List * l);

void printString(String* s);

#define print(a) _Generic(a, int: printInt, short: printShort, struct List *: printList, String*: printString)(a); printf("\n");

#endif