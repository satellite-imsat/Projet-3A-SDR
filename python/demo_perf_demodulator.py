#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_perf_detector.py
@Time    :   2023/03/15 15:07:38
@Author  :   Thomas Aussaguès & Selman Sezgin 
@Version :   1.0
@Contact :   {name.surname}@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès & Selman Sezgin 
@Desc    :   Simulation of the detector + demodulator + decoder
             performance.
'''

"""
This script runs a Monte-Carlo on 1000 signals to assess the demodulato 
performance through BER curve vs. SNR. It also compute errors
on the errors on the AIS data. 
For each characteristic, a plot is made and saved in the results folder.
"""

# Imports
import numpy as np
# AIS processing
from ais_processing.ais import GenAIS
from ais_processing.modulator import Modulator
from ais_processing.channel import AWGN
from ais_processing.demodulator import Demodulator
from ais_processing.detector import Detector
from ais_processing.decoder import Decoder
# Plots
import matplotlib.pyplot as plt
# Progress bar
from tqdm import tqdm

# Signal parameters
# Bitrate in bits/s
C_BITRATE_BITPERSEC = 9600
# Signal duration in s
C_SIGNAL_DURATION = 26.66e-3
# Upsampling factor
C_UPSAMPLING = 10
# Time-Bandwidth product
C_TIME_BANDWIDTH_PROD = 0.4
# Sampling frequency in Hz
C_SAMPLING_FREQUENCY_HZ = C_BITRATE_BITPERSEC * C_UPSAMPLING

# MONTE-CARLO simulations parameters
# SNR values in dB
C_SNR_VALUES_DB = np.arange(-10, 25, 1)
# Number of signals to be generated
C_N_SIGNALS = 100

# Storage arrays (one value for each SNR and each threshold values)
# Binary Error Rate on the detected signal array 
ber_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# Message type error array
msg_type_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# MMSI error array
mmsi_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# Longitude errror array
longitude_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# Latitude error array
latitude_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# Course error array
course_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])
# CRC error array
crc_errors_array = np.zeros(C_SNR_VALUES_DB.shape[0])

# Instanciate relevant object
# Create an AIS generator object
ais_generator = GenAIS()
# Create a GMSK modulator object
gmsk_mod = Modulator(sampling_frequency_hz = C_SAMPLING_FREQUENCY_HZ, 
                    upsampling = C_UPSAMPLING,
                    time_bandwidth_prod = C_TIME_BANDWIDTH_PROD)
# Create a Demodulator object
gmsk_demod = Demodulator() 
# Create a detector object
detector = Detector()
# Create a decoder object
decoder = Decoder()


if __name__ == '__main__':

    for (n_snr, snr_db) in tqdm(enumerate(C_SNR_VALUES_DB)) :

        print("At SNR = ", snr_db, " dB")

        # Create a AWGN channel object
        awgn_channel = AWGN(snr_db, add_phase=True)

        # Initialize the metrics
        position_error = 0
        ber = 0
        msg_type_error = 0.
        mmsi_error = 0.
        longitude_error = 0.
        latitude_error = 0.
        course_error = 0.
        crc_error = 0.

        # Iterate over all signals
        for _ in range(C_N_SIGNALS) :

            # Generate and modulate an AIS signal
            v_ais_bits, data_gt = ais_generator.gen_rand_ais_type_1(return_info=True)
            v_signal_tx = gmsk_mod.mod_signal_gmsk(v_ais_bits[:256])
            # Add noise
            v_signal_rx = awgn_channel.propagate(v_signal_tx)
            
            # Demodulate the signal
            v_signal_demod = gmsk_demod.demod_signal_gmsk(v_signal_rx, C_UPSAMPLING)
            
            # BER
            ber += 1 - np.sum(np.equal(v_signal_demod, v_ais_bits[:256])) / v_signal_demod.shape[0]

            # Decoding
            v_signal_decoded = decoder.decode(v_ais_bits = decoder.nrzi_inv(v_signal_demod))
            decoded_data = decoder.get_data(v_ais_bits = v_signal_decoded)
            # Update errors on the signal content
            msg_type_error += 1 * (decoded_data['msg_type'] != data_gt['msg_type'])
            mmsi_error += 1 * (decoded_data['msg_type'] != data_gt['msg_type'])
            longitude_error += 1 * (abs(decoded_data['longitude'] - data_gt['longitude']) > 1e-3)
            latitude_error += 1 * (abs(decoded_data['latitude'] - data_gt['latitude']) > 1e-3)
            course_error += 1 * (abs(decoded_data['course'] - data_gt['course']) > 1e-3)
            crc_error += 1 * (decoded_data['crc'] == "not correct")
                    
        # Update statistics
        ber_array[n_snr] = ber / C_N_SIGNALS
        msg_type_errors_array[n_snr] = msg_type_error / C_N_SIGNALS
        mmsi_errors_array[n_snr] = mmsi_error / C_N_SIGNALS
        longitude_errors_array[n_snr] = longitude_error / C_N_SIGNALS
        latitude_errors_array[n_snr] = latitude_error / C_N_SIGNALS
        course_errors_array[n_snr] = course_error / C_N_SIGNALS
        crc_errors_array [n_snr] = crc_error / C_N_SIGNALS




    # Plots

    # Plot the BER curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, ber_array, marker = "+")
    plt.grid()
    plt.ylabel("BER")
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.title("BER vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_ber_curves.png", dpi = 300)

    # Plot the message type error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, msg_type_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False message types proportion")
    plt.title("False  message types vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_message_type_error_curves.png", dpi = 300)

    # Plot the MMSI error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, mmsi_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False MMSI proportion")
    plt.title("False MMSI vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_mmsi_error_curves.png", dpi = 300)

    # Plot the longitude error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, longitude_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False longitude proportion")
    plt.title("False longitudes vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_longitude_error_curves.png", dpi = 300)

    # Plot the latitude error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, latitude_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False latitudes proportion")
    plt.title("False latitudes vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_latitude_error_curves.png", dpi = 300)

    # Plot the course error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, course_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False courses proportion")
    plt.title("False courses vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_course_error_curves.png", dpi = 300)


    # Plot the CRC error curves
    plt.figure()
    plt.plot(C_SNR_VALUES_DB, crc_errors_array, marker = "+")
    plt.grid()
    plt.xlabel("Signal to Noise Ratio (in dB)")
    plt.ylabel("False CRC proportion")
    plt.title("False CRC vs. SNR")
    plt.savefig("python/results/perf_demodulator/demodulator_crc_error_curves.png", dpi = 300)

