#ifndef HEADER_DEMOD
#define HEADER_DEMOD

#include <math.h>
#include "complexLib.h"

extern const int sizeSignal;
extern double fporteuse;
extern int timeDelay;
extern double fsample;

void initVectors(double* timePointer, double samplePeriod);
void computeMultSignals(struct complex* inputPointer, double* timePointer);
void computeOutput(double* outputPointer, struct complex* bufferPointer);

#endif