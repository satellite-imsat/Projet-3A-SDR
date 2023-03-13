#ifndef HEADER_BITTREATMENT
#define HEADER_BITTREATMENT

#include "signalCaracteristics.h"
#include <stdlib.h>

void flipBits(int* inputVector, int* output, int size);
void nrziInv(int* inputVector, int size);
void removePreambleFlag(int* inputVector, int* output, int size);
int bitStuffingInv(int* inputVector, int* output, int size);
void removeCheckSum(int* inputVector,int* output, int size);

#endif