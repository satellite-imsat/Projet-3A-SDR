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
# Signal-to-Noise-Ratio in dB (float)
c_snr_db = 10

############################# Signal generation #############################

# We generate a random binary signal
v_signal = random_binary_signal(n_symb = c_n_symb)

# We load a quote and we convert it into a binary signal
# word = pd.read_csv("data/quotes.csv").iloc[0][3]
# v_signal = word_to_binary_signal(word)

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
                                time_bandwidth_product = c_time_bandwidth_product)

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

# Here, we consider a simple AWGN channel with no attenuation

# First we get the signal power defined as the signal squared norm divided by the number of symbols
signal_power = np.linalg.norm(v_signal) ** 2 / v_signal.shape[0]
# Then, we compute the noise power (in linear units) by applying the SNR definition in linear units.
noise_power = signal_power / (10 ** (c_snr_db / 10))
# Finally, we simply add a random complex noise to the signal since we have an AWGN channel.
v_signal_gmsk = v_signal_gmsk + np.sqrt(noise_power / 2) * (np.random.randn(v_signal_gmsk.shape[0]) + 1j * np.random.randn(v_signal_gmsk.shape[0]))

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