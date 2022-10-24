
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
from functions.gen_signal import binary_to_nrz_signal

def gaussian_filter(time_bandwidth_product : float, tb : float, up_sampling_factor : int, filter_length : int) -> np.ndarray :

    '''
    
    This function returns the impulse response of a Gaussian (bell-shaped) filter. It is used
    as a pulse-shaping filter in GMSK.
    
    Inputs :
    
    -> time_bandwidth_product : float, the time bandwidth product, 0.3 for GMSK
    -> tb                     : float, the bit duration is second
    -> filter_length          : int, should at least be one, filter length such that the min time value is
    - filter_length * tb and the max one filter_length * tb
    
    Output :
    
    -> impulse_response, np.ndarray (of shape (2 * up_sampling * filter_length + 1, ) of real values), the filter impulse response
    
    '''

    # We check that the filter lenght is an integer
    if type(filter_length) != int :
        raise ValueError(f"The filter legnth should be a positive integer at least equal to one. Here the type is {type(filter_length)}!")
    
    # We check that the filter length is greater or equal to one
    if filter_length < 1 :
        raise ValueError(f"The filter legnth should be a positive integer at least equal to one. Here, the filter legnth is {filter_length} which is less than one!")

    # We compute the b coefficients
    b = time_bandwidth_product / tb
    # Then, we get the variance
    sigma_squared = np.log(2) / (2 * np.pi * b) ** 2

    # We create a time vector. Note that it contains 2 * up_sampling * filter_length + 1 values.
    v_time = np.arange(start = - filter_length * tb, stop = filter_length * tb + tb / up_sampling_factor, step = tb / up_sampling_factor)
    # Using this vector, we get the filter impulse response
    v_impulse_response = 1 / np.sqrt(2 * np.pi * sigma_squared) * np.exp(- v_time ** 2 / (2 * sigma_squared))
    # We normalize it 
    v_impulse_response /= np.sum(v_impulse_response)

    return v_impulse_response

def mod_signal_gmsk(v_signal : np.ndarray, fc_hz : float, up_sampling_factor : int, time_bandwidth_product : float, **kwargs) -> np.ndarray:

    '''

    This function modulates a binary signal using GMSK modulation. It handles all necessary steps : from the NRZ conversion to applying the
    carrier. The ouput signal is complex.

    Inputs :

    -> v_signal               : np.ndarray (of shape (n_symb, ) of binary values), this array contains the binary signal
    -> fc_hz                  : float (positive, should be non null), the carrier frequency in Hz
    -> up_sampling_factor     : int (positive, at least one), the upsampling factor such that the value of each bit will 
                                remain the same on up_sampling_factor samples
    -> time_bandwidth_product : float (positive, non-null), the time-bandwith value, standard value 0.3
    -> modulation_index       : float (positive, non-null), OPTIONAL parameter, the modulation index h
    -> filter_length          : int (positive, at least one), OPTIONAL parameter, the length of the Gaussian pulse-shaping 
                                filter such that the min time of the impulse response value is
                                - filter_length * tb and the max one filter_length * tb

    Output :

    -> v_signal_gmsk          : np.ndarray (of shape (n_symb * up_sampling_factor, ) of complex floats), this array contains 
                                the values of the modulated signal

    '''

    ## Optional parameters
    modulation_index        = kwargs.get('modulation_index', 0.5)
    filter_length           = kwargs.get('filter_length', 1)

    # If we pass the modulation index, we check that 0 < modulation_index <= 1
    if modulation_index <= 0 or modulation_index > 1 :
        raise ValueError(f"The modulation error should be between 0 and 1 (>0). Here the value {modulation_index} does not satisfy this condition.")

    ## We compute some parameters of the signal
    # Sampling frequency (in Hz)
    fs_hz = up_sampling_factor * fc_hz
    # Sampling time (in s)
    ts_s = 1 / fs_hz
    # Bit duration (in s)
    tb_s = up_sampling_factor * ts_s

    # We remove any useless additional dimension of the signal. We assume that all data is contained on its first
    # dimension
    v_signal = v_signal.squeeze()

    ## Pulse shaping
    # We convert the binary signal to an NRZ one with rectangular pulses
    v_signal = binary_to_nrz_signal(binary_signal = v_signal, up_sampling_factor = up_sampling_factor)
    # Then, we compute the impulse response of the Gaussian pulse-shaping filter
    v_gaussian_filter = gaussian_filter(time_bandwidth_product = time_bandwidth_product, tb = tb_s, up_sampling_factor = up_sampling_factor, filter_length = filter_length).squeeze()
    # We apply it using convolution. Note that we choose to use the "full" mode here.
    v_signal = np.convolve(a = v_signal, v = v_gaussian_filter, mode = "full")
    
    ## Integration
    # Normalisation step 
    v_signal /= np.max(v_signal)
    # Integration step
    v_signal = scipy.signal.lfilter(b = [1], a = [1, -1], x = v_signal * 1 / fs_hz)
    # Multiplication with a constant 
    v_signal *= np.pi * modulation_index / tb_s
    
    ## I & Q components
    # Then, we get both I and Q components (In phase and Quadrature)
    v_i_signal = np.cos(v_signal)
    v_q_signal = np.sin(v_signal)
    # We form the complex GMSK signal : signal = I - j * Q
    gmsk_signal = v_i_signal - 1j *  v_q_signal

    ## Carrier wave
    # We generate a time vector
    v_time = np.arange(start = 0, stop = gmsk_signal.shape[0], step = 1) / fs_hz
    # Finally, we multiply it with the carrier (of frequency fc_hz)
    gmsk_signal *= np.exp(2 * 1j * np.pi * fc_hz * v_time)
 
    return gmsk_signal

def demod_gmsk_signal(v_signal_gmsk : np.ndarray, fc_hz : float, up_sampling_factor : int) -> np.ndarray :

    '''
    
    This function demodulates the input GMSK modulated signal. The input signal is assumed to not be a baseband one.
    
    Inputs :
    
    -> v_signal_gmsk      : np.ndarray (of shape (n_symb * up_sampling_factor, ) of complex floats), this array contains 
                            the values of the modulated signal
    -> fc_hz              : float (positive, should be non null), the carrier frequency in Hz
    -> up_sampling_factor : int (positive, at least one), the upsampling factor such that the value of each bit will 
                            remain the same on up_sampling_factor samples
    
    Output :
    
    -> v_signal_hat       : np.ndarray (of shape (n_symb, ) of binary values), this array contains the estimated binary signal
    
    '''

    # We remove any useless additional dimension of the signal. We assume that all data is contained on its first
    # dimension
    v_signal_gmsk = v_signal_gmsk.squeeze()
    # We get the number of samples n_samples
    n_samples = v_signal_gmsk.shape[0]

    ## Removal the carrier frequency
    # We create a time vector
    v_time = np.arange(start = 0, stop = v_signal_gmsk.shape[0], step = 1) / (fc_hz * up_sampling_factor)
    # We remove the carrier frequency
    v_signal_gmsk = v_signal_gmsk * np.exp( -2 * 1j * np.pi * fc_hz * v_time)
    
    ## I & Q components
    v_i_signal = np.real(v_signal_gmsk)
    v_q_signal = - np.imag(v_signal_gmsk)

    ## Delayed version of the I & Q components
    v_i_signal_delayed = np.hstack((np.zeros(up_sampling_factor), v_i_signal[0 : n_samples - up_sampling_factor]))
    v_q_signal_delayed = np.hstack((np.zeros(up_sampling_factor), v_q_signal[0 : n_samples - up_sampling_factor]))

    # We apply the formula : signal_hat = Q * I_delayed - I * Q_delayed
    signal_hat = v_q_signal * v_i_signal_delayed - v_i_signal * v_q_signal_delayed

    # Decision based on the sign of the estimated signal. If > 0 then its 1 and 0 else.
    # Note that we remove samples added by the upsampling step
    signal_hat = (signal_hat[2 * up_sampling_factor - 1 : - up_sampling_factor : up_sampling_factor] > 0).astype(int)
    
    return signal_hat

