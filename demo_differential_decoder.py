#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_differential_decoder.py
@Time    :   2022/12/27 15:34:32
@Author  :   Thomas Aussaguès 
@Version :   1.0
@Contact :   thomas.aussagues@imt-atlantique.net
@License :   (C)Copyright 2022, Thomas Aussaguès
@Desc    :   None
'''

from signals.gen_signal import random_binary_signal
from modulation.mod_gmsk import mod_signal_gmsk, differential_decoder
from propagation.channels import awgn_channel
import matplotlib.pyplot as plt
import numpy as np
from utils.metrics import compute_ber
import matplotlib.pyplot as plt
plt.style.use(['science','grid'])


############################# Parameters #############################

# We fix the random seed for reproductibility
np.random.seed(1)

# General parameters of the transmitted signal.
# Each parameter name is followed by the corresponding unit.

# AIS signal time length (in s)
c_signal_duration_s = 26.66e-3

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

############################# Signal generation #############################

# Generate a random binary signal
v_signal = random_binary_signal(n_symb = c_n_symb)

# Plot of the generated binary signal
plt.figure('binary_signal')
v_time = np.arange(start = 0, stop = v_signal.shape[0], step = 1) * 1 / c_bit_rate_bit_per_sec
plt.stem(v_time * 1e3, v_signal)
plt.xlim([0, 1 / c_bit_rate_bit_per_sec * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Binary signal')
plt.savefig('figures/demo_gmsk_binary_signal/binary_signal.pdf', dpi = 300)
plt.close('binary_signal')

############################# Signal GMSK modulation #############################

# Modulate the signal
v_signal_tx = mod_signal_gmsk(v_signal = v_signal, 
                            fs_hz = c_fs_hz,
                            up_sampling_factor = c_up_sampling, 
                            time_bandwidth_product = c_time_bandwidth_product)


# Plot of the modulated signal, without noise
plt.figure('unoised_modulated_signal')
v_time = np.arange(start = 0, stop = v_signal_tx.shape[0], step = 1) * 1 / c_fs_hz
plt.plot(v_time * 1e3, np.real(v_signal_tx))
plt.xlim([0, 1 / c_fs_hz * c_up_sampling * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title('Unoised modulated signal')
plt.savefig('figures/demo_gmsk_binary_signal/unoised_modulated_signal.pdf', dpi = 300)
plt.close('unoised_modulated_signal')

# AWGN channel
v_signal_rx = awgn_channel(v_signal = v_signal_tx, snr_db = c_snr_db)

# Plot of the noisy modulated signal
plt.figure('noisy_modulated_signal')
v_time = np.arange(start = 0, stop = v_signal_rx.shape[0], step = 1) * 1 / c_fs_hz
plt.plot(v_time * 1e3, np.real(v_signal_rx))
plt.xlim([0, 1 / c_fs_hz * c_up_sampling * 20 * 1e3])
plt.xlabel('Time $t$ in ms')
plt.ylabel('Signal s(t)')
plt.title(f'Noisy modulated signal, SNR = {c_snr_db} dB')
plt.savefig('figures/demo_gmsk_binary_signal/noisy_modulated_signal.pdf', dpi = 300)
plt.close('noisy_modulated_signal')


########################### Differential decoding ###########################

v_signal_decoded = differential_decoder(v_signal_rx=v_signal_rx, 
                                        up_sampling_factor=c_up_sampling)

############################# Binary Error Rate #############################

# We compute the BER
ber = compute_ber(demodulated_signal =  v_signal_decoded, ground_truth_signal = v_signal)

### Printing results
print('\n', '*' * 60, '\n')
print(f"For a SNR of {c_snr_db} dB, we have a BER of {ber}\n")
print('*' * 60, '\n')