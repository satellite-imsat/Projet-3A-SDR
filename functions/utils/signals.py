#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   gen_signal.py
@Time    :   2022/10/24 18:14:34
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''


import numpy as np
from scipy.signal import upfirdn

def random_binary_signal(n_symb : int) -> np.ndarray:

    '''This function generates a random binary signal. Bit values (0 or 1) are
    equally distributed.

    Input :

    -> n_symb : int, number of bits. Should be at least one

    Output :

    -> binary_signal : np.ndarray (of shape (n_symb, ) of integers (0 and 1)), contains
                       the binary signal
     '''

    # If number of symbols is not an integer
    if type(n_symb) !=  int :
        raise ValueError(f"The number of symbols N should be an integer at least equal to one. Here N = {n_symb} is not an integer!")
    
    # If up_sampling factor is less than one
    if n_symb < 1 :
        raise ValueError(f"The number of symbols N should be an integer at least equal to one. Here N = {n_symb} is less than one!")

    # We generate a random binary stream. The drawn floats are transformed into ones if they are gretaer than .5
    # and 0 elsewhere. Multiplication by one to convert Booleans True/False into integers zero and one.
    binary_signal = 1 * (np.random.rand(n_symb) > .5)

    return binary_signal.astype(int)


def binary_to_nrz_signal(binary_signal : np.ndarray, up_sampling_factor : int) -> np.ndarray :

    '''This function converts an input binary signal to a Non Return to Zero NRZ one using rectangular pulses of length 
    up_sampling_factor (whihc is the discretized bit duration). In other words, each bit corresponds to up_sampling_factor
    samples with values 1 or - 1.

    Inputs :

    -> binary_signal      : np.ndarray (of shape (n_symb, ) of zeros and ones integers), contains the binary signal
    -> up_sampling_factor :

    Output :

    -> nrz_signal         : np.ndarray (of shape (n_symb * up_sampling_factor, ) of plus/minus one integers), 
                            contains the NRZ signal
    '''


    '''The input signal should be a binary one, with only zeros and ones'''

    # If the input signal is not a binary one
    if np.unique(binary_signal).tolist() not in  [[0, 1], [1,0]] :
       
        raise ValueError(f"The input signal is not a binary one. Here it contains the following values {np.unique(binary_signal)}")

    '''The up sampling factor (denoted as rho in the report) should be an integer at least equal to 2. If not (rho = 1),
    NYQUIST's sampling criterion is not fulfilled since the sampling frequency is given 
    by rho * carrier frequency >= carrier frequency.'''

    # If up_sampling factor is not an integer
    if type(up_sampling_factor) !=  int :
        raise ValueError(f"The up sampling factor rho should be an integer at least equal to two. Here rho = {up_sampling_factor} is not an integer!")
    
    # If up_sampling factor is less than two
    if up_sampling_factor < 2 :
        raise ValueError(f"The up sampling factor rho should be an integer at least equal to two. Here rho = {up_sampling_factor} is less than 2!")

    # We shift the binary signal values from [0, 1] to [-1, 1].
    # binary_signal[k] = 1 => 2 * binary_signal[k] - 1 = 1
    # binary_signal[k] = 0 => 2 * binary_signal[k] - 1 = - 1
    nrz_signal = 2 * binary_signal - 1

    # Then, we apply the rectangular waveform to obtain a pulse train
    nrz_signal = upfirdn(h = [1] * up_sampling_factor, x = nrz_signal, up = up_sampling_factor)

    return nrz_signal
