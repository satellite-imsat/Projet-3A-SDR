#include "complexLib.h"

struct complex complexExp(double frequency, double time){
    struct complex exp;
    exp.real = cos(-2*3.14*frequency*time)*1000;
    exp.imag = sin(-2*3.14*frequency*time)*1000;
    return exp;
}

struct complex complexProduct(struct complex a, struct complex b){
    struct complex result;
    result.real = a.real*b.real-a.imag*b.imag;
    result.imag = a.imag*b.real+a.real*b.imag;
    return result;
}

struct complex complexAdd(struct complex a, struct complex b){
    struct complex result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

struct complex complexSoust(struct complex a, struct complex b){
    struct complex result;
    result.real = a.real - b.real;
    result.imag = a.imag - b.imag;
    return result;
}

struct complex complexConjug(struct complex a){
    struct complex result;
    result.real = a.real;
    result.imag = -a.imag;
    return result;
}

double squareNorm(struct complex a){
    return (pow(a.real,2) + pow(a.imag,2));
}

double arg(struct complex a){
    return (atan2(a.imag,a.real));
}

void printComplex(struct complex a){
    printf("%f + i%f \r\n", a.real, a.imag);
}

double squareNormVector(struct complex* a, int sizeVector){
    double sum = 0;
    for(int i =0;i<sizeVector;i++){
        sum += squareNorm(a[i]);
    }
    return sum;
}