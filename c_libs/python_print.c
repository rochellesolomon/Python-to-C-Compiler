#include "python_print.h"

void printInt(int x){
    printf("%d", x);
}

void printShort(short s){
    if(s == 0){
        printf("False");
    }else{
       printf("True"); 
    }
}

void printList(struct List * l){
    struct Node * head = l->head;
    printf("[");
    for (int i = 0; i<l->length; i++){
        if (i!=0){
            printf(", ");
        }
        switch (head->node_type)
        {
        case p_int:
            printf("%d", *((int *)head->data));
            break;
        case p_bool:;
            short val = *((short *) head->data);
            if (val == 0){
                printf("False");
            } else {
                printf("True");
            }
            break;
        case p_list:
            printList(head->data);
            break;
        case p_string:
            printString(head->data);
        default:
            break;
        }
        head = head->next;
    }
    printf("]");
}

void printString(String* s){
    for (int i=0; i<s->length; i++){
        printf("%c", s->data[i]);
    }
}