#ifndef HEADER_DEMOD
#define HEADER_DEMOD

#include <math.h>
#include "complexLib.h"

extern const int sizeSignal;
extern double fporteuse;
extern int timeDelay;
extern double fsample;

void initVectors(double* timePointer, double samplePeriod);
void computeDelayedSignals(struct complex* delayedPointer, struct complex* multPointer, struct complex* inputPointe, double* timePointer);
void computeOutput(double* outputPointer,struct complex* delayedPointer, struct complex* multPointer);

#endif