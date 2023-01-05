#include "demod.h"
#include "complexLib.h"
#include <math.h>
#include <stdio.h>
#include "signalCaracteristics.h"

void initVectors(double* timePointer, double samplePeriod){
    for(int i =0; i<sizeSignal; i++){
        *(timePointer + i)=i*samplePeriod;
    }
    printf("init ok \r\n");
    return;
}

void computeMultSignals(struct complex* inputPointer, double* timePointer){
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

void demodulate(struct complex* inputPointer, double* outputPointer, double fsample, double fporteuse, int timeDelay, int sizeSignal){
    sizeSignal = sizeSignal;
    fporteuse = fporteuse;
    timeDelay = timeDelay;
    fsample = fsample;
    
    initVectors(outputPointer, 1/fsample);
    computeMultSignals(inputPointer,outputPointer);
    computeOutput(outputPointer,inputPointer);

    return;
}


