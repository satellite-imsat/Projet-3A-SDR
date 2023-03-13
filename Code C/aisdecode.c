#include "aisDecode.h"
#include<stdio.h>
int binToDec(int* bitVector, int size);
int twosComplement(int val, int size);

/*
Fonction : getFromMessage
Entrées : vecteur de bits d'entrée, position de départ, position de fin
Sorties : l'entier donné par les bits entre les deux positions dans le vecteur
*/
int getFromMessage(int* inputVector, int start, int end){
    int result = 0;
    int size = end-start;
    int* subMessage = (int*) malloc((size)*sizeof(int));
    for(int i=0;i<size;i++){
        *(subMessage+i)=*(inputVector+start+i);
    }

    result = binToDec(subMessage,size);

    
    free(subMessage);
    return result; 
}


int binToDec(int* bitVector, int size){
    int result = 0;
    for(int i=0;i<size;i++){
        result+=*(bitVector+i)*pow(2,size-1-i);
    }
    return twosComplement(result,size);
}

int twosComplement(int val, int size) {
    int sign_bit = 1 << (size - 1);
    if ((val & sign_bit) != 0) {
        val = val - (1 << size);
    }
    return val;
}