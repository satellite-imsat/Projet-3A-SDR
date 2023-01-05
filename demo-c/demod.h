#ifndef HEADER_DEMOD
#define HEADER_DEMOD

#include <math.h>
#include "complexLib.h"

void demodulate(struct complex* inputPointer,double* outputPointer, double fsample, double fporteuse, int timeDelay, int sizeSignal);

#endif