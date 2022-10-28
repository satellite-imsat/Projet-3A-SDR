#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_gmsk_ais.py
@Time    :   2022/10/27 10:37:51
@Author  :   Thomas Aussaguès & Selman Sezgin
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net, selman.sezgin@imt-atlantique.net,
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''

from signals.gen_ais import get_ais_packet
from modulation.mod_gmsk import mod_signal_gmsk, demod_gmsk_signal
from propagation.channels import awgn_channel, propagation_loss
import matplotlib.pyplot as plt
import numpy as np
from utils.metrics import compute_ber
import matplotlib.pyplot as plt
plt.style.use(['science','grid'])

'''

The purpose of this script is to illustrate the GMSK modulation and demodulation of a AIS signal.
The performance is evaluated through the binary error rate.

Some general notations :
-> A constant value variable begins with a c
-> A vector variables begins with a v

'''
############################# Parameters #############################

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
# Time-bandwidth product (float, 0.4 for AIS)
c_time_bandwidth_product = 0.4

# Desried Signal-to-Noise-Ratio in dB at the RX (float)
c_snr_db = 10

# Antennas parameters

# Output signal power in dB (float) (10 dB <=> 10 W)
c_output_signal_power = 10 
# TX gain in dBi
c_g_tx_dbi = 0
# TX gain in dBi
c_g_rx_dbi = 0
# Distance TX - RX (horizontal and vertical distances in the formule) (km)
c_distance_km = np.sqrt(30 ** 2 + 40 ** 2)

############################# AIS signal #############################

# First, we define the AIS message that we want to transmite
v_ais_msg_str = '!AIVDM,1,1,,B,19NS7Sp02wo?HETKA2K6mUM20<L=,0*27'
# Then, we encode it using a cyclic error correcting code with 16 states
v_ais_msg_binary = get_ais_packet(v_ais_msg_str)

# BUG : THE AIS MESSAGE LENGTH IS 260. HOWEVER ONE AIS SLOT CAN ONLY CONTAIN 255 BITS. 
# BUG : QUESTION : THIS MESSAGE SHOULD BE CONTAINED ON TWO SLOTS OR DO WE HAVE A MISTAKE IN THE GENERATOR (AND SO THE LENGTH IS LESS THAN 256) ?

############################# Signal GMSK modulation #############################

# We modulate the signal
v_signal_gmsk = mod_signal_gmsk(v_signal = v_ais_msg_binary, 
                                fs_hz = c_fs_hz,
                                fc_hz = c_fc_hz, 
                                up_sampling_factor = c_up_sampling, 
                                time_bandwidth_product = c_time_bandwidth_product)

############################# Propgation over the chosen channel #############################

# Propagation loss : we compute the signal power at the RX according to FRIIS' formula
v_signal_gmsk = propagation_loss(v_signal = v_signal_gmsk,
                                tx_power_dB = c_output_signal_power, 
                                g_tx_dBi = c_g_tx_dbi, 
                                g_rx_dBi = c_g_rx_dbi, 
                                carrier_frequency_Mhz = c_fc_hz, 
                                distance_km = c_distance_km)

# AWGN channel : we apply the noise such that the SNR at the RX is c_snr_db
v_signal_gmsk = awgn_channel(v_signal = v_signal_gmsk, snr_db = 10)

############################# Signal GMSK demodulation #############################

# We demodulate the signal
v_hat = demod_gmsk_signal(v_signal_gmsk = v_signal_gmsk,
                          fs_hz = c_fs_hz,
                          fc_hz = c_fc_hz,
                          up_sampling_factor = c_up_sampling)


############################# Decoding (ECC) #############################

# TODO : THE ECC DECODING IS NOT YET IMPLEMENTED!

############################# Binary Error Rate #############################

# We compute the BER
ber = compute_ber(demodulated_signal =  v_hat, ground_truth_signal = v_ais_msg_binary)

### Printing results
print('\n', '*' * 60)
print(f"For a SNR of {c_snr_db} dB, we have a BER of {ber}\n")
print('*' * 60, '\n')
