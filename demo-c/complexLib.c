#include "complexLib.h"
#include <stdio.h>

struct complex complexExp(double frequency, double time){
    struct complex exp;
    exp.real = cos(2*3.14*frequency*time);
    exp.imag = sin(2*3.14*frequency*time);
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
};

void printComplex(struct complex a){
    printf("%f + i%f \r\n", a.real, a.imag);
}