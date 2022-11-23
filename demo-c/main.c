#include <stdio.h>
#include "demod.h"
#include "complexLib.h"
#include <stdlib.h>

const int sizeVectors = 10;
int main()
{
   printf("***** Start of main ***** \r\n");

   struct complex *bufferComplexPointer = (struct complex*) malloc(sizeVectors*sizeof(struct complex));
   double *bufferDoublePointer = (double*) malloc(sizeVectors*sizeof(double));

   // generate random input and test demod
   for(int i = 0; i< sizeVectors; i++){
    (bufferComplexPointer+i)->real=3.0;
    (bufferComplexPointer+i)->imag=7.0;
   }
    demodulate(bufferComplexPointer,bufferDoublePointer,230400,161975000.0,2,sizeVectors);
    for(int i = 0; i< sizeVectors; i++){
        printf("%f \r\n", *(bufferDoublePointer + i));
   }
   free(bufferComplexPointer);
   free(bufferDoublePointer);

   return(0);
}