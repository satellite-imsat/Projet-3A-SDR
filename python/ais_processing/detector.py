#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   detector.py
@Time    :   2023/03/15 11:40:03
@Author  :   Thomas Aussaguès & Selman Sezgin
@Version :   1.0
@Contact :   {name.surname}@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès & Selman Sezgin
@Desc    :   This class implements multiple detection schemes
             in order to detect AIS signals. 
'''


import numpy as np
from math import lgamma

class Detector:

    """
    ==============================
                Detector
    ==============================

    This class implements multiple detection schemes
    (listed below) in order to detect AIS signals. 

    1) Maximum Likelihood Detector: A detector based on 
    the power variation when a signal appears in the noise
    2) Preamble detector: A detector that looks for the 
    AIS preamble and start flag in the demodulated and NRZI
    inverted signal. 

    Attributes
    ----------

    preamble: array-like,
        AIS preamble
    flag: array-like,
        AIS start and stop flags
    detection_sequence: array-like, 
        The dectection sequence
    """

    def __init__(self) -> None:

        # AIS preamble
        self.preamble = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        # AIS start and stop flags
        self.flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])
        # The dectection sequence
        self.detection_sequence = np.concatenate((self.preamble, self.flag))

    def log_likelihood(self, v_ais_signal_rx, t):
        """Return the log-likelihood of the changepoint estimator.

        Parameters
        ----------
        v_ais_signal_rx: array-like
            The input signal which contains a (unique) changepoint.
        t: int
            The changepoint which parameters the likelihood.

        Returns
        -------
        float
            The log-likelihood evaluate at y for the parameter t.
        """
        return -0.5*(t + 5)*np.log(np.sum(v_ais_signal_rx[:t]**2)) -\
            0.5*(v_ais_signal_rx.size - t - 7)*np.log(np.sum(v_ais_signal_rx[t:]**2)) +\
                lgamma(0.5*(t + 5)) + lgamma(0.5*(v_ais_signal_rx.size - t - 3))


    def mle_detector(self, v_ais_signal_rx):
        """Returns an estimation of the changepoint.
        
        Parameters
        ----------
        v_ais_signal_rx: array-like
            The input signal which contains a (unique) changepoint.

        Returns
        -------
        t0_hat: int
            The changepoint estimation, which corresponds to the parameter that
            maximizes the likelihood.
        """
        N = v_ais_signal_rx.size
        likelihoods = []

        for t in range(10, N-10):
            likelihoods.append(self.log_likelihood(v_ais_signal_rx, t))

        t0_hat = np.argmax(likelihoods)

        return t0_hat
    
    def nrzi_inv(self, v_ais_bits : np.ndarray) -> np.ndarray:
        """Invert the non return to zero inversion.

        Parameters
        ----------
        v_ais_bits: array-like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_inv: array-like
            The AIS data bits without non return to zero inversion.
        """
        n = np.size(v_ais_bits)
        v_ais_bits_inv = np.zeros(n)
        state = 0

        for i in range(n):
            if v_ais_bits[i] != state:
                v_ais_bits_inv[i] = 0
                state = v_ais_bits[i]
            else:
                v_ais_bits_inv[i] = 1

        return v_ais_bits_inv

    
    def preamble_detector(self, v_signal_demod : np.ndarray,
                             threshold : int) -> tuple[bool, np.ndarray, int]:
        
        """
        This function implements the detetor proposed in our report
        (Part 1, Chapter 2). It takes a decision on the presence
        of an AIS signal based on the scalar product between the 
        preamble + flag sequence an the corresponding bits in the
        received signal. It processes the signal by blocks of length 
        256.
        
        Paramters
        ---------

        v_signal_demod: np.ndarray,
            The demodulated received signal
        threshold: int
            The detection threshold, between -32
            and 32, can take only even values.
        
        Returns
        -------
        
        bool, 
            A flag saying if a signal has been detected
        best_block: array-like,
            The signal block containing the AIS signal
        best_bloc_index: int
            The corresponding block start position in the 
            signal. The return signal has already undergone 
            NRZI inversion
        """

        
        # Invert the NRZI encoding
        v_signal_demod = self.nrzi_inv(v_ais_bits = v_signal_demod)
        # Maximum starting index for a block of size 256
        n_start_block_max = v_signal_demod.shape[0] - 256
        # Build a matrix such that each row of it contains a block of the signal
        # of size 32 that potentialy contains the preamble and flag
        mat = np.array(
            [v_signal_demod[block_index : block_index + 256][8:40] 
            for block_index in range(0, n_start_block_max)
            ])
            
        # Compute all the inner products 
        inner_products =  (2 * mat - 1) @ (2 * self.detection_sequence - 1)
        # Get the largest one
        best_inner_prod = np.max(inner_products)
        # Corresponding index
        best_block_index = np.argmax(inner_products)
    
        # Detection: if the largest inner product is greater or equal
        # to the threshold
        if best_inner_prod >= threshold:
            # Get the corresponding signal block
            best_block = v_signal_demod[best_block_index : best_block_index + 256]
        else :
            best_block = None

        return (best_block is not None), best_block, best_block_index