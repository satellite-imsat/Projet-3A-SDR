#include <stdio.h>
#include "demod.h"
#include "complexLib.h"
#include <stdlib.h>



int main()
{
   printf("***** Start of main ***** \r\n");
   
   struct complex *bufferComplexPointer = (struct complex*) malloc(sizeSignal*sizeof(struct complex));
   double *bufferDoublePointer = (double*) malloc(sizeSignal*sizeof(double));

   // generate random input and test demod
   for(int i = 0; i< sizeSignal; i++){
    (bufferComplexPointer+i)->real=3.0;
    (bufferComplexPointer+i)->imag=7.0;
   }

   initVectors(bufferDoublePointer, 0.0001);
   for(int i = 0; i< sizeSignal; i++){
    printf("%f \r\n", *(bufferDoublePointer + i));
   }

   computeMultSignals(bufferComplexPointer,bufferDoublePointer);
   for(int i = 0; i< sizeSignal; i++){
    printComplex(*(bufferComplexPointer + i));
   }


   computeOutput(bufferDoublePointer,bufferComplexPointer);
   for(int i = 0; i< sizeSignal; i++){
    printf("%f \r\n", *(bufferDoublePointer + i));
   }

   free(bufferComplexPointer);
   free(bufferDoublePointer);

   return(0);
}