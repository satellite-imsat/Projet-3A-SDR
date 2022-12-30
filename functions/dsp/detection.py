#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   detection.py
@Time    :   2022/12/29 22:01:30
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''

import numpy as np

def correlation_detector(v_signal_rx : np.array, v_signal_ref : np.array, threshold : float, corr = False) -> tuple :

    """
    Implements the correlation detector. The decision is taken by comparing
    the cross-correlation between the received signal and the reference to
    a given threshold. This function returns the decision and the index 
    where the signal starts if it is present. 
    
    Note that the cross-correlation is computed using MATLAB's
    normalization
    
    C_xy[k] <- 1 / (||x|| * ||y||) * C_xy[k]
    
    Parameters
    ----------

    - v_signal_rx : array-like (of complex floats)
        the received signal
    - v_signal_ref : array-like (of complex floats)
        the reference signal
    - threshold : float (between 0 and 1)
        the detector threshold
    - corr : boolean
        if True, the cross-correlation vector is returned


    Returns
    -------

    - decision : boolean
        the taken decision
    - max_index : int
        the index where the signal starts if it is present. 
    - v_corr : array-like
        the computed cross-correlation magnitude 
    """

    # Compute the cross-correlation modulus between the received signal and the
    # reference using MATLAB's normalization
    v_corr = np.correlate(v_signal_rx, v_signal_ref, mode = "same") \
        / (np.linalg.norm(v_signal_rx) * np.linalg.norm(v_signal_ref))
    v_corr = np.abs(v_corr) 

    # Get the max and argmax
    max_corr = np.max(v_corr)
    max_index = np.argmax(v_corr)

    if corr :
        return max_corr > threshold, max_index, v_corr
    
    return max_corr > threshold, max_index