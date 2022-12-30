#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   channels.py
@Time    :   2022/12/29 21:59:47
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''


import numpy as np


def awgn_channel(v_signal : np.ndarray, snr_db : float, n_symb_noise = None):

    '''This function simulates the propagation of a signal through an Additive White Gaussian Noise
    channel. The noise power is computed such that the output signal has the specified SNR value in
    dB. If n_symb_noise is specifided then the signal is placed at a random position in the noise. Else, 
    the noise is simply added to the signal.
    
    Parameters
    ----------
    
    - v_signal : array-like (of complex floats)
        the signal to be transmitted
    - snr_db : float
        the desired SNR

    Returns
    ------
    
    - v_signal_awgn : array_like (of complex floats)
        the noisy signal
    
    '''

    # Signal power : the signal squared norm divided by the number of symbols
    signal_power = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]

    # Noise power (in linear units)
    noise_power = signal_power / (10 ** (snr_db / 10))

    # If n_symb is None, then the noise is simply added to the useful signal
    if n_symb_noise is None :
        
        # Complex noise added to the signal
        v_signal_awgn = v_signal + np.sqrt(noise_power / 2) * (np.random.randn(v_signal.shape[0]) \
            + 1j * np.random.randn(v_signal.shape[0]))

        return v_signal_awgn
    
    # Else, the useful signal is placed at a random position in the noise
    elif n_symb_noise > v_signal.shape[0] :

        # Start position
        start_position = np.random.randint(low = 0, high = n_symb_noise - v_signal.shape[0] + 1)
        # Complex noise 
        v_signal_awgn = np.sqrt(noise_power / 2) * (np.random.randn(n_symb_noise) \
            + 1j * np.random.randn(n_symb_noise))
        # Add the useful signal
        v_signal_awgn[start_position : start_position + v_signal.shape[0]] = v_signal

        return v_signal_awgn, start_position