#ifndef HEADER_COMPLEX
#define HEADER_COMPLEX

#include <math.h>
#include <stdio.h>
struct complex           
{
	float real,imag;     
};

struct complex complexExp(double frequency, double time);
struct complex complexProduct(struct complex a, struct complex b);
struct complex complexAdd(struct complex a, struct complex b);
struct complex complexSoust(struct complex a, struct complex b);
struct complex complexConjug(struct complex a);
double squareNorm(struct complex a);
double arg(struct complex a);
double squareNormVector(struct complex* a, int sizeVector);
void printComplex(struct complex a);

#endif