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

void computeMultSignals(struct complex* inputPointer, double* timePointer){
    printf("here");
    struct complex zeroComplex;
    zeroComplex.real=0.0;
    zeroComplex.imag=0.0;
    for(int i=0; i<sizeSignal; i++){
        *(inputPointer + i)=complexProduct(*(inputPointer + i),complexExp(fporteuse,*(timePointer + i)));
    };
   printf("Mult ok \r\n");
    return;
}

void computeOutput(double* outputPointer,struct complex* bufferPointer){
    for(int i = 0; i< sizeSignal; i++){
         if(i<timeDelay){
            *(outputPointer + i)=0.0;
         } else {
            *(outputPointer + i)=(bufferPointer + i)->real*(bufferPointer + i - timeDelay)->imag + (bufferPointer + i)->imag*(bufferPointer + i - timeDelay)->real;
         }
    }
    printf("output ok \r\n");
    return;
}


