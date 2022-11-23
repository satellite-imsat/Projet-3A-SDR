#include "demod.h"
#include "complexLib.h"
#include <math.h>
#include <stdio.h>

const int sizeSignal = 10;
double fporteuse = 161975000.0;
int timeDelay = 2;
double fsample = 230400;

void initVectors(double* timePointer, double samplePeriod){
    for(int i =0; i<sizeSignal; i++){
        *(timePointer + i)=i*samplePeriod;
    }
    printf("init ok \r\n");
    return;
}

void computeDelayedSignals(struct complex* delayedPointer, struct complex* multPointer, struct complex* inputPointer, double* timePointer){
    printf("here");
    struct complex zeroComplex;
    zeroComplex.real=0.0;
    zeroComplex.imag=0.0;
    for(int i=0; i<sizeSignal; i++){
        *(multPointer + i)=complexProduct(*(inputPointer + i),complexExp(fporteuse,*(timePointer + i)));
        if(i<timeDelay){
            *(delayedPointer + i)=zeroComplex;
        } else {
            *(delayedPointer + i)=*(multPointer + i - timeDelay);
        }
    };
   printf("Delay ok \r\n");
    return;
}

void computeOutput(double* outputPointer,struct complex* delayedPointer, struct complex* multPointer){
    for(int i = 0; i< sizeSignal; i++){
        *(outputPointer + i)=(multPointer + i)->real*(delayedPointer + i)->imag + (multPointer + i)->imag*(delayedPointer + i)->real;
    }
    printf("output ok \r\n");
    return;
}


