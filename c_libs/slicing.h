#ifndef PYTHON_SLICING
#define PYTHON_SLICING
#include "python_string.h"
#include "python_list.h"

struct List* sliceList(struct List* list, int start, int end, int step);
String* sliceString(String* string, int start, int end, int step);

#define slice(a, b, c, d) _Generic(a, struct List *: sliceList, String*: sliceString)(a, b, c, d)
#endif