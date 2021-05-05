#ifndef PYTHON_STRING
#define PYTHON_STRING
#include <stdlib.h>

typedef struct python_string
{
    int length;
    char* data;
} String;

String* new_string();
void stringInsert(String* s, char c);
String* concat_strings(String* a, String* b);

#endif
