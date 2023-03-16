#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demodulator.py
@Time    :   2023/03/15 12:27:26
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès
@Desc    :   This class implements an GMSK demodulator. It also provides a
             function to remove frequency shifts
'''

import numpy as np

class Demodulator:

    """
    ==============================
            GMSK Demodulator
    ==============================

    This class implements an GMSK demodulator. It also provides a
    function to remove frequency shifts.

    References
    ----------
    [1] 
    [2]
    """
    

    def compensate_freq_shift(self, v_signal_rx : np.ndarray, sampling_freq_hz : np.ndarray) -> np.ndarray :
        """This function computes the frequency shift of a baseband signal 
        and compensates it.

        Paramters
        ---------

        v_signal_rx: array-like
            the received signal
        sampling_freq_hz: float
            the signal sampling frequency in Hz

        Returns
        -------

        v_signal_rx: array-like
            the corrected received signal
        """

        # FFT computation
        v_signal_rx_dsp = np.abs(np.fft.fftshift(np.fft.fft(v_signal_rx))) ** 2
        # Number of points in the FFT
        n_fft = v_signal_rx_dsp.shape[0]
        # Compute the corresponding frequency vector in Hz
        freq_hz_vec = np.linspace(-0.5, 0.5, n_fft) * sampling_freq_hz
        # Get the spectrum central frequency as weighted average (by the spectrum)
        # of the frequency
        freq_shift_hz = 1 / np.sum(v_signal_rx_dsp) * np.sum(v_signal_rx_dsp * freq_hz_vec)
        
        # Time vector in s
        v_time_s = np.arange(0, v_signal_rx.shape[0]) / sampling_freq_hz
        # Apply the frequency shift in the time domain
        v_signal_rx *= np.exp(-2j*np.pi * freq_shift_hz * v_time_s) 
       
        return v_signal_rx


    
    def demod_signal_gmsk(self, v_signal_rx : np.ndarray, up_sampling_factor : int) -> np.ndarray :
        """Implement a differential decoder that 
        takes a complex baseband signal as input.

        Parameters
        ----------

        v_signal_rx : array-like (of complex floats)
            contains the baseband received signal  
        up_sampling_factor : int
            the upsampling factor

        Returns
        -------

        v_signal_decoded : array-like (of binary int)
            the demodulated signal 
        """

        # Create a delayed version by the upsmapling factor of v_signal_rx
        v_signal_delayed = np.hstack(
            (np.zeros(up_sampling_factor),
            v_signal_rx[0: v_signal_rx.shape[0]-up_sampling_factor])
            )
        # Multiply the conjugated delayed signal with the base signal
        v_multiplied_signal = v_signal_rx * np.conj(v_signal_delayed)

        # Get the phase of the resulting signal
        v_phase = np.angle(v_multiplied_signal)
        # Downsampling
        v_phase = v_phase[2*up_sampling_factor-1:-up_sampling_factor:up_sampling_factor]
        # Extract bits from the pahse sign
        v_signal_decode = (v_phase<0).astype(np.int8)

        return v_signal_decode