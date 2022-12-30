#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_detection.py
@Time    :   2022/12/30 14:16:22
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''


import numpy as np

from functions.dsp.detection import correlation_detector
from functions.utils.signals import random_binary_signal
from functions.ais.gen_ais import gen_rand_ais_type_1, non_return_to_zero_inversion
from functions.dsp.modulation import mod_signal_gmsk
from functions.dsp.channels import awgn_channel

from functions.utils.plots import plot_correlation_detector_output
from functions.utils.miscellaneous import bool_to_colored_str

import matplotlib.pyplot as plt
plt.style.use(['science','grid'])

from prettytable import PrettyTable

############################# Parameters #############################

# General parameters of the transmitted signal.
# Each parameter name is followed by the corresponding unit.

# AIS signal time length (in s)
c_signal_duration_s = 26.66e-3

# AIS ramp-up bits
v_ais_ramp_up = np.zeros(8)

# AIS start and stop flag
v_ais_flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])

# AIS preamble
v_ais_preamble = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])

# AIS buffer bits
v_ais_buffer = np.zeros(24)

# Bitrate used in AIS communcations (float)
c_bit_rate_bit_per_sec = 9600

# Number of symbols (integer, greater than 0)
c_n_symb = int(c_bit_rate_bit_per_sec * c_signal_duration_s)

# Upsampling factor  (integer, greater than 2) 
# => the sampling frequency is c_bit_rate_bit_per_sec * c_up_sampling
c_up_sampling = 24

# Sampling frequency
c_fs_hz = c_bit_rate_bit_per_sec * c_up_sampling

# Time-bandwidth product (float, 0.4 for AIS)
c_time_bandwidth_product = 0.4

# Desried Signal-to-Noise-Ratio in dB at the RX (float)
c_snr_db = 5

c_threshold = 0.3

############################### AIS references ###############################

# AIS first bits : reference for signal detection
v_ais_ref_start = np.hstack((v_ais_ramp_up, v_ais_preamble, v_ais_flag))
v_ais_ref_start = non_return_to_zero_inversion(ais_data_bit = v_ais_ref_start)

v_ais_start_tx = mod_signal_gmsk(v_signal = v_ais_ref_start, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product)

# AIS last bits : reference for stopping the buffering
v_ais_ref_stop = np.hstack((v_ais_flag, v_ais_buffer))
v_ais_ref_stop = non_return_to_zero_inversion(ais_data_bit = v_ais_ref_stop)

v_ais_ref_stop_tx = mod_signal_gmsk(v_signal = v_ais_ref_stop, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product) 



############################### Signal 1 : AIS ###############################

# Generate a random AIS message and the associated packet
v_signal1 = gen_rand_ais_type_1()
 
# Modulate the signal
v_signal_tx1 = mod_signal_gmsk(v_signal = v_signal1, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product)

# AWGN channel
v_signal_rx1, start_position = awgn_channel(v_signal = v_signal_tx1, snr_db = c_snr_db, n_symb_noise = c_up_sampling * c_n_symb * 2)

# Start detection
start_is_present_rx1, start_rx1, v_corr_start_rx1 = correlation_detector(v_signal_rx=v_signal_rx1,v_signal_ref=v_ais_start_tx, threshold=c_threshold, corr=True)

# Stop detection 
stop_is_present_rx1, stop_rx1, v_corr_stop_rx1 = correlation_detector(v_signal_rx=v_signal_rx1,v_signal_ref=v_ais_ref_stop_tx, threshold=c_threshold, corr=True)

# Correlation plot
plot_correlation_detector_output(v_corr_start = v_corr_start_rx1, 
                                v_corr_stop = v_corr_stop_rx1, 
                                threshold = c_threshold, 
                                fs_hz = c_fs_hz, 
                                start_pos = start_position, 
                                end_pos = start_position + v_signal1.shape[0] * c_up_sampling, 
                                title = f"In presence of an AIS signal, SNR = {c_snr_db} dB", 
                                name = f"with_ais_snr_{c_snr_db}_db")

############################### Signal 2 : GMSK without AIS ###############################

# Generate a random binary signal
v_signal2 = random_binary_signal(n_symb = c_n_symb)

# Modulate the signal
v_signal_tx2 = mod_signal_gmsk(v_signal = v_signal2, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product)

# AWGN channel
v_signal_rx2, _ = awgn_channel(v_signal = v_signal_tx2, snr_db = c_snr_db, n_symb_noise = c_up_sampling * c_n_symb * 2)

# Start detection
start_is_present_rx2, start_rx2, v_corr_start_rx2 = correlation_detector(v_signal_rx=v_signal_rx2,v_signal_ref=v_ais_start_tx, threshold=c_threshold, corr=True)

# Stop detection 
stop_is_present_rx2, stop_rx2, v_corr_stop_rx2 = correlation_detector(v_signal_rx=v_signal_rx2,v_signal_ref=v_ais_ref_stop_tx, threshold=c_threshold, corr=True)

# Correlation plot
plot_correlation_detector_output(v_corr_start = v_corr_start_rx2, 
                                v_corr_stop = v_corr_stop_rx2, 
                                threshold = c_threshold, 
                                fs_hz = c_fs_hz, 
                                start_pos = None, 
                                end_pos = None,
                                title = f"GMSK signal, SNR = {c_snr_db} dB", 
                                name = f"gmsk_{c_snr_db}_db")     

############################### Signal 3 : Noise only ###############################

v_signal_rx3 = 1 / np.sqrt(2) * (np.random.randn(c_up_sampling * c_n_symb * 2) + 1j * np.random.randn(c_up_sampling * c_n_symb * 2))


# Start detection
start_is_present_rx3, start_rx3, v_corr_start_rx3 = correlation_detector(v_signal_rx=v_signal_rx3,v_signal_ref=v_ais_start_tx, threshold=c_threshold, corr=True)

# Stop detection 
stop_is_present_rx3, stop_rx3, v_corr_stop_rx3 = correlation_detector(v_signal_rx=v_signal_rx3,v_signal_ref=v_ais_ref_stop_tx, threshold=c_threshold, corr=True)

# Correlation plot
plot_correlation_detector_output(v_corr_start = v_corr_start_rx3, 
                                v_corr_stop = v_corr_stop_rx3, 
                                threshold = c_threshold, 
                                fs_hz = c_fs_hz, 
                                start_pos = None, 
                                end_pos = None,
                                title = f"Noise", 
                                name = f"noise")     

############################### Printing results ###############################

results_table = [
    ["Signal / Ref.", "AIS", "GMSK", "Noise"], 
    ["Start", bool_to_colored_str(start_is_present_rx1), bool_to_colored_str(start_is_present_rx2), bool_to_colored_str(start_is_present_rx3)],
    ["Stop", bool_to_colored_str(stop_is_present_rx1), bool_to_colored_str(stop_is_present_rx2), bool_to_colored_str(stop_is_present_rx3)]
    ]

table = PrettyTable(results_table[0])
table.add_rows(results_table[1:])

print("*" * 30, '\n', 'Results', '\n')
print(table)




