#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_gmsk_modulation.py
@Time    :   2022/10/24 18:14:50
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022$, Thomas Aussaguès
@Desc    :   None
'''

from signals.gen_signal import random_binary_signal, binary_to_nrz_signal
from modulation.mod_gmsk import mod_signal_gmsk, demod_gmsk_signal
from propagation.channels import awgn_channel, propagation_loss
import matplotlib.pyplot as plt
import numpy as np
from utils.metrics import compute_ber
import matplotlib.pyplot as plt
plt.style.use(['science','grid'])

'''
The purpose of this script is to illustrate the GMSK modulation and demodulation of a random (or not) signal.
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

############################# Signal generation #############################

# We generate a random binary signal
v_signal = random_binary_signal(n_symb = c_n_symb)

## We plot the generated binary signal
plt.figure('binary_signal')
v_time = np.arange(start = 0, stop = v_signal.shape[0], step = 1) * 1 / c_bit_rate_bit_per_sec
plt.stem(v_time * 1e3, v_signal)
plt.xlim([0, 1 / c_bit_rate_bit_per_sec * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Binary signal')
plt.savefig('figures/demo_gmsk_binary_signal/binary_signal.pdf', dpi = 300)
plt.close('binary_signal')

## We plot the NRZ associated signal
plt.figure('nrz_signal')
v_time = np.arange(start = 0, stop = v_signal.shape[0] * c_up_sampling, step = 1) * 1 / c_fs_hz
plt.plot(v_time * 1e3, binary_to_nrz_signal(binary_signal = v_signal, up_sampling_factor = c_up_sampling))
plt.xlim([0, 1 / c_fs_hz * c_up_sampling * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('NRZ signal')
plt.savefig('figures/demo_gmsk_binary_signal/nrz_signal.pdf', dpi = 300)
plt.close('nrz_signal')

############################# Signal GMSK modulation #############################

# We modulate the signal
v_signal_gmsk = mod_signal_gmsk(v_signal = v_signal, 
                                fs_hz = c_fs_hz,
                                fc_hz = c_fc_hz, 
                                up_sampling_factor = c_up_sampling, 
                                time_bandwidth_product = c_time_bandwidth_product,
                                output_power = c_output_signal_power)

## We plot the modulated, without noise, signal
plt.figure('unoised_modulated_signal')
v_time = np.arange(start = 0, stop = v_signal_gmsk.shape[0], step = 1) * 1 / c_fs_hz
plt.plot(v_time * 1e3, np.real(v_signal_gmsk * np.exp(- 2 * 1j * np.pi * c_fc_hz * v_time)))
plt.xlim([0, 1 / c_fs_hz * c_up_sampling * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Unoised modulated signal (no carrier)')
plt.savefig('figures/demo_gmsk_binary_signal/unoised_modulated_signal.pdf', dpi = 300)
plt.close('unoised_modulated_signal')

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

## We plot the noisy modulated signal
plt.figure('noisy_modulated_signal')
v_time = np.arange(start = 0, stop = v_signal_gmsk.shape[0], step = 1) * 1 / c_fs_hz
plt.plot(v_time * 1e3, np.real(v_signal_gmsk * np.exp( - 2 * 1j * np.pi * c_fc_hz * v_time)))
plt.xlim([0, 1 / c_fs_hz * c_up_sampling * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Noisy modulated signal (no carrier)')
plt.savefig('figures/demo_gmsk_binary_signal/noisy_modulated_signal.pdf', dpi = 300)
plt.close('noisy_modulated_signal')

############################# Signal GMSK demodulation #############################

# We demodulate the signal
v_hat = demod_gmsk_signal(v_signal_gmsk = v_signal_gmsk,
                          fs_hz = c_fs_hz,
                          fc_hz = c_fc_hz,
                          up_sampling_factor = c_up_sampling)

############################# Binary Error Rate #############################

# We compute the BER
ber = compute_ber(demodulated_signal =  v_hat, ground_truth_signal = v_signal)

### Printing results
print('\n', '*' * 60, '\n')
print(f"For a SNR of {c_snr_db} dB, we have a BER of {ber}\n")
print('*' * 60, '\n')