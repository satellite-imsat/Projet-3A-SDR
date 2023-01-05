#ifndef HEADER_DETECTOR
#define HEADER_DETECTOR
#include <math.h>
#include "complexLib.h"

extern int sizeKnownSignal;

int signalPresent(struct complex* inputSignal, struct complex* knownSignal, double treshold);

#endif