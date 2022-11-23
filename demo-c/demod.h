#ifndef HEADER_DEMOD
#define HEADER_DEMOD

#include <math.h>
#include "complexLib.h"

extern int sizeSignal;
extern double fporteuse;
extern int timeDelay;
extern double fsample;

void demodulate(struct complex* inputPointer,double* outputPointer, double fsample, double fporteuse, int timeDelay, int sizeSignal);

#endif