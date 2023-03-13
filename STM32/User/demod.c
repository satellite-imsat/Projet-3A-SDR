#include "demod.h"

/*
Fonction : delayVector
Entrées : vecteur complexe avec données, vecteur complexe pour recevoir données retardées
Sorties : 
Permet de retarder le vecteur d'entrée pour le calcul de la démodulation
*/
void delayVector(struct complex* inputVector,struct complex* delayedVector){
    struct complex zeroComplex;
    zeroComplex.real=0;
    zeroComplex.imag=0;
    for(int i=0; i<sizeSignal; i++){
        if(i<timeDelay){
            *(delayedVector + i)=zeroComplex;
        } else {
            *(delayedVector + i)=*(inputVector + i - timeDelay);  
        }   
    }
}

/*
Fonction : computeMultSignals
Entrées : vecteur complexe avec données, vecteur complexe avec données retardées
Sorties : 
Permet de calculer la multiplication entre les deux signaux
*/
void computeMultSignals(struct complex* inputVector,struct complex* delayedVector){ 
    for(int i=0; i<sizeSignal; i++){
        *(inputVector + i)=complexProduct(complexConjug(*(inputVector + i)),*(delayedVector + i));    
    }
    return;
}

/*
Fonction : computeOutput
Entrées : vecteur complexe avec données, vecteur d'entiers avec les bits calculés
Sorties : 
Permet de calculer les bits de sortie en fonction du signal d'entrée
*/
void computeOutput(int* output,struct complex* buffer){
    int positionOutput = 0;
    for(int i = 2*timeDelay-1; i<sizeSignal-timeDelay; i+=timeDelay){
        if(arg(*(buffer+i))>0){
            *(output+positionOutput)=1;
        } else {
            *(output+positionOutput)=0; 
        }
        positionOutput += 1;
    }
    return;
}

/*
Fonction : demodulate
Entrées : vecteur complexe avec données, vecteur complexe pour recevoir données retardées, vecteur d'entiers avec les bits calculés
Sorties : 
Permet de calculer la démodulation du signal d'entrée
*/
void demodulate(struct complex* inputVector,struct complex* delayedVector, int* output){
    delayVector(inputVector,delayedVector);
    computeMultSignals(inputVector,delayedVector);
    computeOutput(output,inputVector);
    return;
}


