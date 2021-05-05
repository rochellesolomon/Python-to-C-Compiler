#include <stdlib.h>
#include "python_list.h"

struct List * new_list(){
    struct List * nl = (struct List *) malloc(sizeof(struct List));
    return nl;
}

void insert(struct List * head, struct Node * node){
    if (head->length == 0){
        head->head = node;
    } else {
        struct Node * slot = head->head;
        for (int i = 0; i<head->length-1; i++){
            slot = slot->next;
        }
        slot->next = node;
    }
    head->length++;
}

void pushInt(struct List* head, int val) {
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
    void* data = malloc(sizeof(int));
    new_node->data = data;
    new_node->next = NULL;
    new_node->node_type = p_int;
    *((int *) data) = val;

    insert(head, new_node);
}

void pushShort(struct List* head, short val) {
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
    void* data = malloc(sizeof(short));
    new_node->data = data;
    new_node->next = NULL;
    new_node->node_type = p_bool;
    *((short*)data) = val;

    insert(head, new_node);
}

void pushList(struct List* head, struct List * val) {
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
    new_node->data = val;
    new_node->next = NULL;
    new_node->node_type = p_list;
    

    insert(head, new_node);
}

void pushString(struct List* head, String * val) {
    struct Node* new_node = (struct Node*)malloc(sizeof(struct Node));
    new_node->data = val;
    new_node->next = NULL;
    new_node->node_type = p_string;
    insert(head, new_node);
}

void extend_list(struct List* to, struct List* from){
    struct Node * head = from->head;
    for (int i = 0; i<from->length; i++){
        switch (head->node_type)
        {
        case p_int:
            pushInt(to, *((int *)head->data));
            break;
        case p_bool:;
            short val = *((short *) head->data);
            pushShort(to, val);
            break;
        case p_list:
            pushList(to, head->data);
            break;
        case p_string:
            pushString(to, head->data);
            break;
        default:
            break;
        }
        head = head->next;
    }
}

struct Node* getNode(struct List* from, int pos){
    if (pos < 0){
        pos = from->length+pos;
    }
    if (pos+1 > from->length){
        printf("Index %d is out of bounds for list\n", pos);
        exit(1);
    }
    struct Node * head = from->head;
    for (int i=0; i<pos; i++){
        head = head->next;
    }
    return head;
}

int getInt(struct List* from, int pos){
    struct Node * node = getNode(from, pos);
    if (node->node_type != p_int){
        fprintf(stderr, "List element %d is not of type int", pos);
    }
    return *((int *)node->data);
}

short getShort(struct List* from, int pos){
    struct Node * node = getNode(from, pos);
    if (node->node_type != p_bool){
        fprintf(stderr, "List element %d is not of type short", pos);
    }
    return *((short *)node->data);
}

struct List * getList(struct List* from, int pos){
    struct Node * node = getNode(from, pos);
    if (node->node_type != p_list){
        fprintf(stderr, "List element %d is not of type list", pos);
    }
    return (struct List *)node->data;
}

String * getStringFromList(struct List* from, int pos){
    struct Node * node = getNode(from, pos);
    if (node->node_type != p_string){
        fprintf(stderr, "List element %d is not of type string", pos);
    }
    return (String *)node->data;
}

String * getStringFromString(String* from, int pos){
    if (pos < 0){
        pos = from->length+pos;
    }
    if (pos+1 > from->length){
        printf("Index %d is out of bounds for string\n", pos);
        exit(1);
    }
    String* s = new_string();
    stringInsert(s, from->data[pos]);
    return s;
}

struct List* concat_lists(struct List* list1, struct List* list2) {
    struct List* nl = new_list();
    extend_list(nl, list1);
    extend_list(nl, list2);
    return nl;
}