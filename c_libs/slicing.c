#include "slicing.h"
struct List* sliceList(struct List* list, int start, int end, int step) {
    struct List * nl = new_list();
    if (start < 0){
        start = 0;
    }
    if (end < 0){
        end = list->length+end;
    }
    if (end > list->length){
        end = list->length;
    }
    if (step < 0){
        for (int i = end-1; i>=start; i += step) {
            struct Node* node = getNode(list, i);
            struct Node* new_node = (struct Node*)malloc(sizeof (struct Node*));
            new_node->node_type = node->node_type;
            new_node->data = node->data;
            new_node->next = NULL;
            insert(nl, new_node);
        }
    }else {
        for (int i = start; i<end; i += step) {
            struct Node* node = getNode(list, i);
            struct Node* new_node = (struct Node*)malloc(sizeof (struct Node*));
            new_node->node_type = node->node_type;
            new_node->data = node->data;
            new_node->next = NULL;
            insert(nl, new_node);
        }
    }
    return nl;
}

String* sliceString(String* string, int start, int end, int step) {
    String * ns = new_string();
    if (start < 0){
        start = 0;
    }
    if (end < 0){
        end = string->length+end;
    }
    if (end > string->length){
        end = string->length;
    }
    if (step < 0){
        for (int i = end-1; i>=start; i += step) {
            stringInsert(ns, string->data[i]);
        }
    }else {
        for (int i = start; i<end; i += step) {
            stringInsert(ns, string->data[i]);
        }
    }
    return ns;
}