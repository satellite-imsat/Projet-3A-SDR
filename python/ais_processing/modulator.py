#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   modulator.py
@Time    :   2023/03/14 22:32:53
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès
@Desc    :   A class that implements a python GMSK modulator
'''

import numpy as np
from scipy.signal import lfilter, upfirdn

class Modulator:

    """
    ==============================
            GMSK Modulator
    ==============================

    This class implements an GMSK modulator. It implements function
    to apply the NRZ conversion, the gaussian filtering and the 
    modulation.

    Attributes
    ----------

    sampling_frequency_hz: float,
        the signal sampling frequency in Hz
    upsampling: int,
        the signal upsampling factor
    time_bandwidth_prod: float,
        the ime bandwidth product
    filter_length: int, default 1
        the gaussian filter lengthf such that the min time value is
        filter_length * tb and the max one filter_length * tb
    modulation_index: int, default 0.5
        the GMSK modulation index
    symbol_duration_s: float,
        the duration of one symbol in s

    References
    ----------
    [1] 
    [2]
    [3]
    """

    def __init__(self, sampling_frequency_hz : float,
                 upsampling : int,
                 time_bandwidth_prod : float,
                 filter_length : int = 1,
                 modulation_index : float = .5
                 ) -> None:

        # Sampling frequency in Hz
        self.sampling_frequency_hz = sampling_frequency_hz
        # Upsampling factor
        self.upsampling = upsampling
        # Time-Bandwidth product
        self.time_bandwidth_prod = time_bandwidth_prod
        # Filter legnth, default 1
        self.filter_length = filter_length
        # Modulation index, default 0.5
        self.modulation_index = modulation_index
        # Symbol duration
        self.symbol_duration_s = 1 / self.sampling_frequency_hz \
            * self.upsampling

    def binary_to_nrz_signal(self, v_binary_signal : np.ndarray) -> np.ndarray :

        """This function converts an input binary signal 
        to a Non Return to Zero NRZ one using rectangular 
        pulses of length up_sampling_factor (which is the 
        discretized symbol duration). In other words, 
        each bit corresponds to up_sampling_factor
        samples with values 1 or - 1.

        Parameters :
        -----------

        v_binary_signal: array-like (of shape (n_symb, ) 
            of zeros and ones integers), 
            contains the binary signal

        Returns :
        ---------

        v_nrz_signal: array-like (of shape (n_symb * 
            up_sampling_factor, ) of plus/minus one integers), 
            contains the NRZ signal
        """


        # We shift the binary signal values from [0, 1] to [-1, 1].
        # binary_signal[k] = 1 => 2 * binary_signal[k] - 1 = 1
        # binary_signal[k] = 0 => 2 * binary_signal[k] - 1 = - 1
        nrz_signal = 2 * v_binary_signal - 1

        # Then, we apply the rectangular waveform to obtain a pulse train
        nrz_signal = upfirdn(h = [1] * self.upsampling, x = nrz_signal, up = self.upsampling)

        return nrz_signal


    def get_filter_resp(self) -> np.ndarray :

        """Returns the impulse response of a Gaussian (bell-shaped) 
        filter. It is used as a pulse-shaping filter in GMSK.
        

        Parameters
        ----------

        see the class' attributes

        Returns
        -------
        
        v_impulse_response: array-like (of shape (2 * up_sampling * 
            filter_length + 1, ), floats), the filter impulse response
        """

        # Variance
        b = self.time_bandwidth_prod / self.symbol_duration_s
        sigma_squared = np.log(2) / (2 * np.pi * b) ** 2

        # Time vector  (2 * up_sampling * filter_length + 1 values)
        v_time = np.arange(start = - self.filter_length * self.symbol_duration_s,
                           stop = self.filter_length * self.symbol_duration_s +\
                           self.symbol_duration_s / self.upsampling,
                           step = self.symbol_duration_s / self.upsampling
                           )
        # Impulse response
        v_impulse_response = 1 / np.sqrt(2 * np.pi * sigma_squared) * np.exp(- v_time ** 2 / (2 * sigma_squared))
        # Normalization
        v_impulse_response /= np.sum(v_impulse_response)

        return v_impulse_response
    
    def mod_signal_gmsk(self, v_signal : np.ndarray) -> np.ndarray:

        """Computes a GMSK modulated of the input signal. 
        The output signal is complex.

        Parameters
        ----------

        v_signal: array-like,
            the signal to modulate
        
        Returns
        -------

        v_signal_tx: array-like (of length n_symb * up_sampling_factor, complex floats), 
            this array contains the values of the modulated signal"""
        
        ## Pulse shaping
        # NRZ signal conversion
        v_signal = self.binary_to_nrz_signal(v_binary_signal = v_signal)
        # Gaussian filter impulse response
        v_impulse_response = self.get_filter_resp()
        # Filtering
        v_signal = np.convolve(v_signal, v_impulse_response, mode = "full")
        
        ## Integration
        # Normalisation step 
        v_signal /= np.max(v_signal)
        # Integration step
        v_signal = lfilter(b = [1], a = [1, -1], x = v_signal * 1 / self.sampling_frequency_hz)
        # Multiplication with a constant 
        v_signal *= np.pi * self.modulation_index / self.symbol_duration_s
        
        ## I & Q components
        # I component
        v_i_signal = np.cos(v_signal)
        # Q component
        v_q_signal = np.sin(v_signal)
        # Complex GMSK signal : signal = I - j * Q
        v_signal_tx = v_i_signal - 1j *  v_q_signal
    
        return v_signal_tx


