#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   channel.py
@Time    :   2023/03/14 22:35:45
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès
@Desc    :   A class that implements an AWGN channel with the possibility
             to add a random phase to the signal and to place randomly
             within the noise.
'''

import numpy as np

class AWGN:

    """
    ==============================
              AWGN channel
    ==============================

    This class implements an AWGN channel with the possibility
    to add a random phase to the signal and to place randomly
    within the noise.

    Attributes
    ----------
    snr_db : float
        the desired SNR
    n_symb_noise : int, default None
        the number generated noise symbols. Sould be greater or equal to
        the signal length. Default value: None => the number of noise symbols
        equals the signal length
    add_phase : boolean, default false
        specifies if a uniformly distirbuted random phase
        over [0, 2\pi] should be added to the signal

    """

    def __init__(self, snr_db, n_symb_noise = None, add_phase = False) -> None:

    
        # Signal to Noise Ratio in dB
        self.snr_db = snr_db
        # Add a random to the signal
        self.add_phase = add_phase
        # Total number of symbol
        self.n_symb_noise = n_symb_noise
        

    def propagate(self, v_signal_tx : np.ndarray) -> np.ndarray:

        '''This function simulates the propagation of a signal through an 
        Additive White Gaussian Noise channel. The noise power is computed 
        such that the output signal has the specified SNR value in dB. 
        If n_symb_noise is specifided then the signal is placed at a random 
        position in the noise. Else, the noise is simply added to the signal.
        The add_phase options adds a random uniformly distirbuted phase over 
        [0, 2\pi] to the signal.
        
        Parameters
        ----------
        
        v_signal_tx : array-like (of complex floats)
            the signal to be transmitted
        

        Returns
        ------
        
        v_signal_awgn : array_like (of complex floats)
            the noisy signal
        start_position: int
            the signal position in noise (if n_symb_noise is not
            None)
        
        '''

        # Signal power: the signal square norm divided by the number of symbols
        signal_power = np.linalg.norm(v_signal_tx) ** 2 / v_signal_tx.shape[0]

        # Random phase: if add_pahse is True, a random phase is added
        if self.add_phase :

            # Uniformly distributed phase over [0, 2\pi]...
            theta = np.random.ranf() * 2 * np.pi
            # ...added to the signal
            v_signal_tx = v_signal_tx * np.exp(1j * theta)

        # Noise power (in linear units)
        noise_power = signal_power / (10 ** (self.snr_db / 10))

        # If n_symb is None: then the noise is simply added to the useful signal
        if self.n_symb_noise is None :
            
            # Complex noise added to the signal
            v_signal_awgn = v_signal_tx + np.sqrt(noise_power / 2) * (np.random.randn(v_signal_tx.shape[0]) \
                + 1j * np.random.randn(v_signal_tx.shape[0]))

            return v_signal_awgn
        
        # Else: the useful signal is placed at a random position in the noise
        elif self.n_symb_noise > v_signal_tx.shape[0] :

            # Start position
            start_position = np.random.randint(low = 0, high = self.n_symb_noise - v_signal_tx.shape[0] + 1)
            # Complex noise 
            v_signal_awgn = np.sqrt(noise_power / 2) * (np.random.randn(self.n_symb_noise) \
                + 1j * np.random.randn(self.n_symb_noise))
            # Add the useful signal
            v_signal_awgn[start_position : start_position + v_signal_tx.shape[0]] += v_signal_tx

            return v_signal_awgn, start_position