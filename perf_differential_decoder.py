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
from functions.ais.gen_ais import gen_rand_ais_type_1
from functions.dsp.modulation import mod_signal_gmsk, differential_decoder
import matplotlib.pyplot as plt
import numpy as np
from functions.dsp.channels import awgn_channel
from functions.utils.metrics import compute_ber
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


# Time-bandwidth product values (float, 0.4 for AIS)
v_time_bandwidth_product = np.arange(start = 0.1, stop = 0.6, step = 0.1)

# Signal-to-Noise-Ratio values in dB (float)
v_snr_db = np.arange(start = 0, stop = 20, step = 2)

# Monte-Carlo simulation paramter : number of generated signals per SNR value
c_n_signals = 1000

# We define a list which will contain one list of BER values per SNR values, for each time-bandwidth product values
results = []

for time_bandwidth_product in v_time_bandwidth_product :

    v_ber = []

    for snr_db in v_snr_db :
    
        running_ber = 0

        for _ in range(c_n_signals) :

            # Generate a random AIS message and the associated packet
            v_signal = gen_rand_ais_type_1()

            ### GMSK modulation ###
            v_signal_gmsk = mod_signal_gmsk(v_signal = v_signal, 
                                            fs_hz = c_fs_hz,
                                            up_sampling_factor = c_up_sampling, 
                                            time_bandwidth_product = time_bandwidth_product)

            #### Propgation over the chosen channel
            
            # AWGN channel : we apply the noise such that the SNR at the RX is snr_db
            v_signal_rx = awgn_channel(v_signal = v_signal_gmsk, snr_db = snr_db)
            
            ### GMSK demodulation ###
            v_signal_decoded = differential_decoder(v_signal_rx=v_signal_rx, 
                                        up_sampling_factor=c_up_sampling)
            
            ### Binary Error Rate  
            running_ber += compute_ber(demodulated_signal = v_signal_decoded, ground_truth_signal = v_signal)

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
plt.savefig('figures/test_gmsk_performance_awgn/ber_vs_snr.pdf', dpi = 300)