#include "python_string.h"
String* new_string(){
    String* s = (String*)malloc(sizeof(String));
    s->length = 0;
    s->data = NULL;
    return s;
}

void stringInsert(String* s, char c){
    char* n = (char*)malloc(sizeof(char)*(s->length+1));
    int i = 0;
    for (; i<s->length; i++){
        n[i] = s->data[i];
    }
    n[i] = c;
    free(s->data);
    s->data = n;
    s->length++;
}

String* concat_strings(String* a, String* b){
    String* ns = new_string();
    for (int i=0; i<a->length;i++){
        stringInsert(ns, a->data[i]);
    }
    for (int i=0; i<b->length;i++){
        stringInsert(ns, b->data[i]);
    }
    return ns;
}
