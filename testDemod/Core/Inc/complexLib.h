#ifndef HEADER_COMPLEX
#define HEADER_COMPLEX

#include <math.h>
struct complex           
{
	double real,imag;     
};

struct complex complexExp(double frequency, double time);
struct complex complexProduct(struct complex a, struct complex b);
struct complex complexAdd(struct complex a, struct complex b);
struct complex complexSoust(struct complex a, struct complex b);
void printComplex(struct complex a);

#endif