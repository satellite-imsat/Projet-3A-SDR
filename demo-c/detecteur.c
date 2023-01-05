#include "detecteur.h"
#include "complexLib.h"
#include "signalCaracteristics.h"

struct complex sumOverN(int n0, struct complex* inputSignal, struct complex* knownSignal){
    struct complex sum;
    for(int i = n0; i<n0+sizeKnownSignal; i++){
        sum = complexAdd(sum,complexProduct(inputSignal[i], knownSignal[i-n0]));
    }
    return sum;
}

int signalPresent(struct complex* inputSignal, struct complex* knownSignal, double treshold){
    double max = 0.0;
    double buffer = 0.0;
    int index = 0;
    for(int i = 0; i<sizeSignal-sizeKnownSignal; i++){
        buffer = squareNorm(sumOverN(i,inputSignal,knownSignal));
        if(buffer>max){
            max = buffer;
            index = i;
        }
    }
    max = max/(sqrt(squareNormVector(inputSignal,sizeSignal))*sqrt(squareNormVector(knownSignal,sizeKnownSignal)));
    if (max > treshold){
        return index;
    } else {
        return -1;
    }
}