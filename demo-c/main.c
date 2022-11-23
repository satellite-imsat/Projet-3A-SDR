#include <stdio.h>
#include "demod.h"
#include "complexLib.h"



int main()
{
   printf("***** Start of main ***** \r\n");
   struct complex testVector[sizeSignal];
   struct complex *testPointer;
   
   double timeVector[sizeSignal];
   double* timeVectorPointer;

   struct complex multVector[sizeSignal];
   struct complex *multPointer;

   struct complex delayedVector[sizeSignal];
   struct complex *delayedPointer;

   double outputVector[sizeSignal];
   double *outputPointer;

   testPointer = testVector;
   timeVectorPointer = timeVector;
   multPointer = multVector;
   delayedPointer = delayedVector;
   outputPointer = outputVector;

   // generate random input and test demod
   for(int i = 0; i< sizeSignal; i++){
    testVector[i].real=3.0;
    testVector[i].imag=7.0;
   }

   initVectors(timeVectorPointer, 0.0001);
   for(int i = 0; i< sizeSignal; i++){
    printf("%f \r\n", *(timeVectorPointer + i));
   }

   computeDelayedSignals(delayedPointer,multPointer,testPointer,timeVectorPointer);
   for(int i = 0; i< sizeSignal; i++){
    printComplex(*(delayedPointer + i));
   }
   computeOutput(outputPointer,delayedPointer,multPointer);
   for(int i = 0; i< sizeSignal; i++){
    printf("%f \r\n", *(outputPointer + i));
   }

   return(0);
}