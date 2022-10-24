#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   test_gmsk_performance_awgn.py
@Time    :   2022/10/24 18:15:11
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''

import numpy as np
from functions.gen_signal import random_binary_signal
from functions.mod_gmsk import mod_signal_gmsk, demod_gmsk_signal
import matplotlib.pyplot as plt
import numpy as np
from functions.metrics import compute_ber
import matplotlib.pyplot as plt

### We fix the random seed for reproductibility
np.random.seed(1)

### We define some general parameters of the transmitted signal.###
# Each parameter name is followed by the corresponding unit.

# Signals paramters

# Number of symbols (integer, greater than 0)
c_n_symb = 100000
# Upsampling factor  (integer, greater than 2)
c_up_sampling = 16
# Carrier frequency (in Hertz)
c_fc_hz = 800
# Time-bandwidth product (float, 0.3 for GMSK)
c_time_bandwidth_product = 0.3
# Signal-to-Noise-Ratio values in dB (float)
v_snr_db_list = np.arange(start = 0, stop = 20, step = 2)

# Monte-Carlo simulation paramter

# Number of generated signals per SNR value
c_n_signals = 1

v_ber_list = []

for snr_db in v_snr_db_list :

    print(snr_db)

    running_ber = 0

    for _ in range(c_n_signals) :

        print(_)

        v_signal = random_binary_signal(n_symb = c_n_symb)

        v_signal_gmsk = mod_signal_gmsk(v_signal = v_signal, 
                                fc_hz = c_fc_hz, 
                                up_sampling_factor = c_up_sampling, 
                                time_bandwidth_product = c_time_bandwidth_product)

        # First we get the signal power defined as the signal squared norm divided by the number of symbols
        # which is the upsampled signal length divided by the upsmapling factor.
   
        # Then, we compute the noise power (in linear units) by applying the SNR definition in linear units.
        noise_power = signal_power / (10 ** (snr_db / 10))
        # Finally, we simply add a random complex noise to the signal since we have an AWGN channel.
        v_signal_gmsk = v_signal_gmsk + np.sqrt(noise_power / 2) * (np.random.randn(v_signal_gmsk.shape[0]) + 1j * np.random.randn(v_signal_gmsk.shape[0]))

        ### Signal GMSK demodulation ###

        v_hat = demod_gmsk_signal(v_signal_gmsk, c_fc_hz, c_up_sampling)
        #v_hat_hat = gmsk_demod(v_signal_gmsk, c_up_sampling)
        ### Binary Error Rate 

        running_ber += compute_ber(demodulated_signal = v_hat, ground_truth_signal = v_signal)

    v_ber_list.append(running_ber / c_n_signals)

plt.figure()
plt.semilogy(v_snr_db_list, v_ber_list)
plt.savefig('figures/test.pdf', dpi = 300)