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
This script runs a Monte-Carlo on 1000 signals to assess the detector 
performance through ROC curves for multiple SNR values. It also compute errors
on the time of arrival, the BER, and errors on the AIS data. 
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
C_SNR_VALUES_DB = np.arange(10, 25, 5)
# Number of signals to be generated
C_N_SIGNALS = 10
# Thresholds values (from -30 (31 errors) to 32 (0 error))
C_THRESHOLD_VALUES = np.arange(-30, 34, 2)

# Storage arrays (one value for each SNR and each threshold values)
# False alarms array
false_alarms_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# True positives array
power_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Absolute error on the AIS signal position array
position_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Binary Error Rate on the detected signal array 
ber_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Message type error array
msg_type_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# MMSI error array
mmsi_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Longitude errror array
longitude_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Latitude error array
latitude_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# Course error array
course_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))
# CRC error array
crc_errors_array = np.zeros((C_SNR_VALUES_DB.shape[0], C_THRESHOLD_VALUES.shape[0]))

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
        awgn_channel = AWGN(snr_db, n_symb_noise = int(256 * C_UPSAMPLING * 1.1))

        for (n_threshold, threshold) in tqdm(enumerate(C_THRESHOLD_VALUES)) :

    
        
            # Initialize the metrics
            false_alarms = 0.
            power = 0.
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


                ## Null hypothesis

                # Random binary signal
                v_signal_demod = np.ones(255 * C_UPSAMPLING * 2) * (np.random.randn(255 * C_UPSAMPLING * 2) > 0)
                # Detection
                is_ais, _, _ = detector.preamble_detector(v_signal_demod = v_signal_demod, threshold = threshold)
                # Statistics
                if is_ais :
                    # False alarm update
                    false_alarms += 1

                ## Alternative hypothesis

                # Generate and modulate an AIS signal
                v_ais_bits, data_gt = ais_generator.gen_rand_ais_type_1(return_info=True)
                v_signal_tx = gmsk_mod.mod_signal_gmsk(v_ais_bits[:256])
                # Add noise
                v_signal_rx, pos_gt = awgn_channel.propagate(v_signal_tx)
                
                # Demodulate the signal
                v_signal_demod = gmsk_demod.demod_signal_gmsk(v_signal_rx, C_UPSAMPLING)
                # Detection
                is_ais, v_block, block_index = detector.preamble_detector(
                   v_signal_demod=v_signal_demod, threshold=threshold)

                # Statistics
                if is_ais :
                    # Power update
                    power += 1
                    # Absolute error on position
                    position_error = + abs(block_index - pos_gt / 10)
                    # BER
                    ber += np.sum(1 - np.equal(v_block, v_ais_bits[:256])) / v_block.shape[0]
                    # Decoding
                    v_signal_decoded = decoder.decode(v_ais_bits = v_block)
                    decoded_data = decoder.get_data(v_ais_bits = v_signal_decoded)
                    # Update errors on the signal content
                    msg_type_error += 1 * (decoded_data['msg_type'] != data_gt['msg_type'])
                    mmsi_error += 1 * (decoded_data['msg_type'] != data_gt['msg_type'])
                    longitude_error += 1 * (abs(decoded_data['longitude'] - data_gt['longitude']) > 1e-3)
                    latitude_error += 1 * (abs(decoded_data['latitude'] - data_gt['latitude']) > 1e-3)
                    course_error += 1 * (abs(decoded_data['course'] - data_gt['course']) > 1e-3)
                    crc_error += 1 * (decoded_data['crc'] == "not correct")
                    
                        

            # False alarm probability and power
            false_alarms_array[n_snr, n_threshold] = false_alarms / C_N_SIGNALS
            power_array[n_snr, n_threshold] = power / C_N_SIGNALS
            # Position error, BER and signals data are computed among the correctly
            # detected signals
            position_errors_array[n_snr, n_threshold] = position_error / power
            ber_array[n_snr, n_threshold] = ber / power
            msg_type_errors_array[n_snr, n_threshold] = msg_type_error / power
            mmsi_errors_array[n_snr, n_threshold] = mmsi_error / power
            longitude_errors_array[n_snr, n_threshold] = longitude_error / power
            latitude_errors_array[n_snr, n_threshold] = latitude_error / power
            course_errors_array[n_snr, n_threshold] = course_error / power
            crc_errors_array [n_snr, n_threshold]= crc_error / power




    # Plots

    # Plot the ROC curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(false_alarms_array[n_snr, :], power_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("False alarm probability")
    plt.ylabel("Power")
    plt.title("Detector ROC curves")
    plt.savefig("python/results/perf_detector/detector_roc_curves.png", dpi = 300)

    # Plot the position error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, position_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("Absolute error (bits)")
    plt.title("Absolute error on position vs. threshold")
    plt.savefig("python/results/perf_detector/detector_position_error_curves.png", dpi = 300)

    # Plot the BER curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, ber_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("BER")
    plt.title("BER vs. threshold")
    plt.savefig("python/results/perf_detector/detector_ber_curves.png", dpi = 300)

    # Plot the message type error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, msg_type_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False message types proportion")
    plt.title("False  message types vs. threshold")
    plt.savefig("python/results/perf_detector/detector_message_type_error_curves.png", dpi = 300)

    # Plot the MMSI error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, mmsi_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False MMSI proportion")
    plt.title("False MMSI vs. threshold")
    plt.savefig("python/results/perf_detector/detector_mmsi_error_curves.png", dpi = 300)

    # Plot the longitude error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, longitude_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False longitude proportion")
    plt.title("False longitudes vs. threshold")
    plt.savefig("python/results/perf_detector/detector_longitude_error_curves.png", dpi = 300)

    # Plot the latitude error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, latitude_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False latitudes proportion")
    plt.title("False latitudes vs. threshold")
    plt.savefig("python/results/perf_detector/detector_latitude_error_curves.png", dpi = 300)

    # Plot the course error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, course_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False courses proportion")
    plt.title("False courses vs. threshold")
    plt.savefig("python/results/perf_detector/detector_course_error_curves.png", dpi = 300)


    # Plot the CRC error curves
    plt.figure()
    for n_snr in range(C_SNR_VALUES_DB.shape[0]):
       plt.plot(C_THRESHOLD_VALUES, crc_errors_array[n_snr, :], 
                marker = "+", label = str(C_SNR_VALUES_DB[n_snr]) + " dB")
    plt.grid()
    plt.legend(loc="best")
    plt.xlabel("Threshold")
    plt.ylabel("False CRC proportion")
    plt.title("False CRC vs. threshold")
    plt.savefig("python/results/perf_detector/detector_crc_error_curves.png", dpi = 300)

