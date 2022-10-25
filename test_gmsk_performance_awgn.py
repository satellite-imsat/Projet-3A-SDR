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
plt.style.use(['science','grid'])

### We fix the random seed for reproductibility
np.random.seed(1)

############################# Parameters #############################

### We define some general parameters of the transmitted signal
# Each parameter name is followed by the corresponding unit.

# Signals paramters

# We fix the random seed for reproductibility
np.random.seed(1)

# We define some general parameters of the transmitted signal.
# Each parameter name is followed by the corresponding unit.

# AIS signal time length (in s)
c_signal_duration_s = 26.66e-3
# Bitrate used in AIS communcations (float)
c_bit_rate_bit_per_sec = 9600
# Number of symbols (integer, greater than 0)
c_n_symb = int(c_bit_rate_bit_per_sec * c_signal_duration_s)
# Upsampling factor  (integer, greater than 2) => the sampling frequency is c_bit_rate_bit_per_sec * c_up_sampling
c_up_sampling = 24
# Sampling frequency
c_fs_hz = c_bit_rate_bit_per_sec * c_up_sampling
# Carrier frequency (in Hertz) (channel A 161.975 MHz (87B) or channel B 162.025 MHz (88B))
c_fc_hz = 161.975e6
# Time-bandwidth product values (float, 0.4 for AIS)
v_time_bandwidth_product = np.arange(start = 0.1, stop = 0.6, step = 0.1)
# Signal-to-Noise-Ratio values in dB (float)
v_snr_db = np.arange(start = 0, stop = 20, step = 1)

# Monte-Carlo simulation paramter : number of generated signals per SNR value
c_n_signals = 100

# We define a list which will contain one list of BER values per SNR values, for each time-bandwidth product values
results = []

for time_bandwidth_product in v_time_bandwidth_product :

    v_ber = []

    for snr_db in v_snr_db :

        running_ber = 0

        for _ in range(c_n_signals) :

            # We generate a random signal
            v_signal = random_binary_signal(n_symb = c_n_symb)

            ### GMSK modulation ###
            v_signal_gmsk = mod_signal_gmsk(v_signal = v_signal, 
                                            fs_hz = c_fs_hz,    
                                            fc_hz = c_fc_hz, 
                                            up_sampling_factor = c_up_sampling, 
                                            time_bandwidth_product = time_bandwidth_product)

            # First we get the signal power defined as the signal squared norm divided by the number of symbols
            signal_power = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]
            # Then, we compute the noise power (in linear units) by applying the SNR definition in linear units.
            noise_power = signal_power / (10 ** (snr_db / 10))
            # Finally, we simply add a random complex noise to the signal since we have an AWGN channel.
            v_signal_gmsk = v_signal_gmsk + np.sqrt(noise_power / 2) * (np.random.randn(v_signal_gmsk.shape[0]) + 1j * np.random.randn(v_signal_gmsk.shape[0]))

            ### GMSK demodulation ###
            v_hat = demod_gmsk_signal(v_signal_gmsk = v_signal_gmsk, 
                                      fs_hz = c_fs_hz, 
                                      fc_hz = c_fc_hz, 
                                      up_sampling_factor = c_up_sampling)
            
            ### Binary Error Rate  
            running_ber += compute_ber(demodulated_signal = v_hat, ground_truth_signal = v_signal)

        v_ber.append(running_ber / c_n_signals)

    results.append(v_ber)

# We plot the results
plt.figure()
for i, time_bandwidth_product in enumerate(v_time_bandwidth_product) :
    plt.semilogy(v_snr_db, results[i], label = f'BT = {time_bandwidth_product :.1f}',marker = '+')
plt.xlabel("SNR (in dB)")
plt.ylabel("Binary Error Rate")
plt.title("GMSK BER vs. SNR")
plt.legend(loc = 'best')
plt.savefig('figures/ber_vs_snr.pdf', dpi = 300)