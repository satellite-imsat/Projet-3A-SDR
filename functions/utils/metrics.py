#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   metrics.py
@Time    :   2022/10/24 18:13:57
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''


import numpy as np

def compute_ber(demodulated_signal : np.ndarray, ground_truth_signal : np.ndarray) -> float :

    '''Given two signals : the ground truth one and the demodulated one, this function 
    computes the binary error rate.
    
    Inputs :
    
    -> demodulated_signal  : np.ndarray (of shape (n_symb, ) of zeros and ones), contains the demodulated signal
    -> ground_truth_signal : np.ndarray (of shape (n_symb, ) of zeros and ones), contains the ground truth signal
    
    Output :
    
    -> ber                 : float (between 0 and 1), bianry error rate'''

    # If signals have different shapes
    if demodulated_signal.shape != ground_truth_signal.shape :
        raise ValueError(f"Shape mismatch : both signals should have the same shape. Here, they have shapes {demodulated_signal.shape} != {ground_truth_signal.shape}")

    # The BER is simply given by the number of symbols for which demodulated_signal != ground_truth_signal 
    # divided by the total number of symbols ie the mean of the array demodulated_signal != ground_truth_signal
    ber = np.mean(demodulated_signal != ground_truth_signal)

    return ber