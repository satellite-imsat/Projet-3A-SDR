#include "bitTreatment.h"

int arrayEqualOne(int* input, int size);

/*
Fonction : flipBits
Entrées : vecteur de bits d'entrée, vecteur de bits pour recevoir la sortie, taille du vecteur de sortie
Sorties : 
Renverse les bits du signal d'entrée
*/
void flipBits(int* inputVector, int* output, int size){
    for(int i=0; i<size; i += 8){
        for(int j = 0; j<8; j++){
            *(output+i+j)=*(inputVector+i+7-j);
        }
    }
}

/*
Fonction : nrziInv
Entrées : vecteur de bits d'entrée, taille du vecteur
Sorties : 
Inverse l'inversion de non retour à zéro
*/
void nrziInv(int* inputVector,int size){
    int state = 0;
    for(int i=0; i<size; i ++){
        if(*(inputVector+i)!=state){
            state=*(inputVector+i);
            *(inputVector+i)=0;
        } else {
            *(inputVector+i)=1;
        }
    }
}

/*
Fonction : removePreambleFlag
Entrées : vecteur de bits d'entrée, vecteur de bits pour recevoir la sortie, taille du vecteur de sortie
Sorties : 
Retire les flags de début et de fin de signal
*/
void removePreambleFlag(int* inputVector, int* output, int size){
    for(int i=0; i<size; i++){
        *(output+i)=*(inputVector+i+sizePreambleFlag);
    }

}

/*
Fonction : bitStuffingInv
Entrées : vecteur de bits d'entrée, vecteur de bits pour recevoir la sortie, taille du vecteur de sortie
Sorties : la nouvelle taille du vecteur de sortie
Inverse l'opération de bit stuffing
*/
int bitStuffingInv(int* inputVector,int* output, int size){
    int n_cons = 5;
    int i = n_cons - 1;
    int i0 = 0;
    int indexOut = 0;
    while(i < size){
        int *subarray = (int*) malloc((n_cons)*sizeof(int));
        for(int j = 0; j<n_cons;j++){
            *(subarray+j)=*(inputVector+i+j-(n_cons-1));
        }
        if(arrayEqualOne(subarray,n_cons)){
            for(int j = i0; j<i+1;j++){
                *(output+indexOut)=*(inputVector+j);
                indexOut += 1;
            }
            i0 = i+2;
            i += n_cons +1;
        }
        else {
            i += 1;
        }
        free(subarray);
    }
    for(int j=i0; j<size; j++){
        *(output+indexOut)=*(inputVector+j);
        indexOut += 1;
    }
    return indexOut;
}

int arrayEqualOne(int* input, int size){
    for(int i = 0; i<size; i++){
        if(*(input+i)!=1){
            return 0;
        }
    }
    return 1;
}

/*
Fonction : removeCheckSum
Entrées : vecteur de bits d'entrée, vecteur de bits pour recevoir la sortie, taille du vecteur de sortie
Sorties : 
Retire la check sum du signal
*/
void removeCheckSum(int* inputVector, int* output, int size){
    for(int i=0; i<size; i++){
        *(output+i)=*(inputVector+i);
    }
}
