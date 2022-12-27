#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   mod_gmsk.py
@Time    :   2022/10/24 17:35:04
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''

# Imports
import numpy as np
import scipy.signal
# We import the binary_to_nrz_signal function which converts a binary signal
# (0's and 1's) to an NRZ one (-1's and 1's) and applied a rectangular pulse shaping filter
from signals.gen_signal import binary_to_nrz_signal

def gaussian_filter(time_bandwidth_product : float, tb : float, up_sampling_factor : int, filter_length : int) -> np.ndarray :

    '''
    
    Return the impulse response of a Gaussian (bell-shaped) filter. It is used
    as a pulse-shaping filter in GMSK.
    
    Parameters
    ----------
    
    - time_bandwidth_product : float
        time bandwidth product, 0.3 for GMSK
    - tb : float
        the bit duration is second
    - filter_length : int
        should at least be one, filter length such that the min time value is
        filter_length * tb and the max one filter_length * tb
    
    Returns
    -------
    
    - impulse_response : array-like (of shape (2 * up_sampling * filter_length + 1, ), floats)
        the filter impulse response
    
    '''

    # We check that the filter lenght is an integer
    if type(filter_length) != int :
        raise ValueError(f"The filter legnth should be a positive integer at least equal to one. Here the type is {type(filter_length)}!")
    
    # We check that the filter length is greater or equal to one
    if filter_length < 1 :
        raise ValueError(f"The filter legnth should be a positive integer at least equal to one. Here, the filter legnth is {filter_length} which is less than one!")

    # Filter coefficients
    b = time_bandwidth_product / tb
    # Variance
    sigma_squared = np.log(2) / (2 * np.pi * b) ** 2

    # Time vector  (2 * up_sampling * filter_length + 1 values)
    v_time = np.arange(start = - filter_length * tb, stop = filter_length * tb + tb / up_sampling_factor, step = tb / up_sampling_factor)
    # Impulse response computation
    v_impulse_response = 1 / np.sqrt(2 * np.pi * sigma_squared) * np.exp(- v_time ** 2 / (2 * sigma_squared))
    # Normalization
    v_impulse_response /= np.sum(v_impulse_response)

    return v_impulse_response

def mod_signal_gmsk(v_signal : np.ndarray, fs_hz : float, up_sampling_factor : int, time_bandwidth_product : float, **kwargs) -> np.ndarray:

    '''
    Implementation of GMSK modulation. The output signal is complex.

    Parameters
    ----------

    - v_signal : array-like (of length n_symb, binary int),
        contains the binary signal
    - fs_hz : float 
        sampling frequency in Hz
    - up_sampling_factor     : int 
        upsampling factor such that the value of each bit will remain 
        the same on up_sampling_factor samples
    - time_bandwidth_product : float,
        the time-bandwith value, standard value 0.3
    - modulation_index : float, 
        optional, the modulation index h
    - filter_length : int (positive, at least one), 
        optional, the length of the Gaussian pulse-shaping 
        filter such that the min time of the impulse response value is
        - filter_length * tb and the max one filter_length * tb

    Returns
    -------

    - v_signal_gmsk : array-like (of length n_symb * up_sampling_factor, complex floats), 
        this array contains the values of the modulated signal

    '''

    ## Optional parameters

    modulation_index        = kwargs.get('modulation_index', 0.5)
    filter_length           = kwargs.get('filter_length', 1)

    # If we pass the modulation index, we check that 0 < modulation_index <= 1
    if modulation_index <= 0 or modulation_index > 1 :
        raise ValueError(f"The modulation error should be between 0 and 1 (>0). Here the value {modulation_index} does not satisfy this condition.")

    ## Bit duration
    # Sampling time (in s)
    ts_s = 1 / fs_hz
    # Bit duration (in s)
    tb_s = up_sampling_factor * ts_s

    # We remove any useless additional dimension of the signal. We assume that all data is contained on its first
    # dimension
    v_signal = v_signal.squeeze()

    ## Pulse shaping
    
    # NRZ signal conversion
    v_signal = binary_to_nrz_signal(binary_signal = v_signal, up_sampling_factor = up_sampling_factor)
    # Gaussian filter impulse response
    v_gaussian_filter = gaussian_filter(time_bandwidth_product = time_bandwidth_product, tb = tb_s, up_sampling_factor = up_sampling_factor, filter_length = filter_length).squeeze()
    # Filtering
    v_signal = np.convolve(a = v_signal, v = v_gaussian_filter, mode = "full")
    
    ## Integration
    
    # Normalisation step 
    v_signal /= np.max(v_signal)
    # Integration step
    v_signal = scipy.signal.lfilter(b = [1], a = [1, -1], x = v_signal * 1 / fs_hz)
    # Multiplication with a constant 
    v_signal *= np.pi * modulation_index / tb_s
    
    ## I & Q components

    # I component
    v_i_signal = np.cos(v_signal)
    # Q component
    v_q_signal = np.sin(v_signal)
    # Complex GMSK signal : signal = I - j * Q
    v_signal_tx = v_i_signal - 1j *  v_q_signal
 
    return v_signal_tx

def differential_decoder(v_signal_rx : np.ndarray, up_sampling_factor : int) -> np.ndarray :

    """
    Implement a differential decoder that takes a complex baseband signal as input.

    Parameters
    ----------

    - v_signal_rx : array-like (of complex floats)
        contains the baseband received signal  
    - up_sampling_factor : int
        the upsampling factor

    Returns
    -------

    - v_signal_decoded : array-like (of binary int)
        the demodulated signal 
    """

    # Delayed signal of the symbol duration 
    v_signal_delayed = np.hstack((np.zeros(up_sampling_factor), v_signal_rx[0 : v_signal_rx.shape[0] - up_sampling_factor]))

    # Multiplication between conj(x(t)) and x(t-T) where T is the symbol duration
    v_multiplied_signal = np.conj(v_signal_rx) * v_signal_delayed

    # Phase difference extraction
    v_phase = np.angle(v_multiplied_signal)

    # Downsampling
    v_phase = v_phase[2 * up_sampling_factor - 1 : - up_sampling_factor : up_sampling_factor]

    # Bits estimation based on the phase difference sign
    v_signal_decoded = (v_phase > 0).astype(np.int8)

    return v_signal_decoded





