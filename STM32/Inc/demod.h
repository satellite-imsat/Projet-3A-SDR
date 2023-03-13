#ifndef HEADER_DEMOD
#define HEADER_DEMOD

#include <math.h>
#include "complexLib.h"
#include "signalCaracteristics.h"

void demodulate(struct complex* inputVector,struct complex* delayedVector, int* output);

#endif