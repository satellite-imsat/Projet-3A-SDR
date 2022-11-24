#include "complexLib.h"
#include <stdio.h>
#include "main.h"

UART_HandleTypeDef huart2handler;

struct complex complexExp(double frequency, double time){
    struct complex exp;
    exp.real = cos(-2*3.14*frequency*time);
    exp.imag = sin(-2*3.14*frequency*time);
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
	uint8_t data[10];
	double value=a.real;
	snprintf(data, 10, "%f", value);
	HAL_UART_Transmit (&huart2handler, data, sizeof (data), 10);

	uint8_t inter[]=" + i";
	HAL_UART_Transmit (&huart2handler, inter, sizeof (inter), 10);

	value=a.imag;
	snprintf(data, 10, "%f", value);
	HAL_UART_Transmit (&huart2handler, data, sizeof (data), 10);

	uint8_t space[]="\r\n";
	HAL_UART_Transmit (&huart2handler, space, sizeof (space), 10);

}
