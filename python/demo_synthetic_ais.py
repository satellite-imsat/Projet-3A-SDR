#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   demo_synthetic_ais.py
@Time    :   2023/03/15 14:20:07
@Author  :   Thomas Aussaguès & Selman Sezgin
@Version :   1.0
@Contact :   {name.surname}@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès & Selman Sezgin
@Desc    :   A script to illustrate the proposed demodulator for processing
             AIS signals on synthetic data
'''

"""
This script test the proposed architecture on synthtic AIS data that is generated
using both our custom module and PyAIS. Then, the signal is modulated and passed
through an AWGN channel that adds a random phase to it. Finally, detection and
decoding is run to retrieve the signal data.
"""

# Imports
from ais_processing.ais import GenAIS
from ais_processing.modulator import Modulator
from ais_processing.channel import AWGN
from ais_processing.demodulator import Demodulator
from ais_processing.detector import Detector
from ais_processing.decoder import Decoder

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
# Signal to Noise ratio in dB
C_SNR_DB = 20

# Threshold for the detection. Set to 32 => 0 error on the preamble + start flag
# sequence
C_DETECTION_THRESHOLD = 32

if __name__=='__main__':

    print("\n**** AIS processing example on synthetic data ****\n")
 
    ##################### Signal generation #####################
    # AIS generaotr object
    ais_generator = GenAIS()
    # Generate a random type 1 AIS message and get the corresponding
    # data
    v_ais_bits, data = ais_generator.gen_rand_ais_type_1(return_info = True)
    # Print sent data
    print('\nSent data\n')
    print(f"Message Type    : {data['msg_type']}")
    print(f"MMSI            : {data['mmsi']}")
    print(f"Longitude (deg) : {data['longitude']}")
    print(f"Latitude (deg)  : {data['latitude']}")
    print(f"Course (deg)    : {data['course']}\n")

    ##################### Modulation #####################
    # Modulator object
    modulator = Modulator(sampling_frequency_hz = C_SAMPLING_FREQUENCY_HZ, 
                          upsampling = C_UPSAMPLING, 
                          time_bandwidth_prod = C_TIME_BANDWIDTH_PROD)
    # Apply GMSK modulation to the signal
    v_signal_tx = modulator.mod_signal_gmsk(v_signal = v_ais_bits)

    ##################### AWGN channel #####################
    # AWGN channel object
    awgn_channel = AWGN(snr_db = C_SNR_DB, 
                        n_symb_noise = int(1.25 * v_signal_tx.shape[0]), 
                        add_phase = True)
    # Pass the signal through an AWGN channel
    v_signal_rx, _ = awgn_channel.propagate(v_signal_tx = v_signal_tx)

    ##################### Demodulator #####################
    demodulator = Demodulator()
    v_signal_demodulated = demodulator.demod_signal_gmsk(
        v_signal_rx = v_signal_rx, up_sampling_factor = C_UPSAMPLING)

    
    ####################### Detection #######################
    # Detector object
    detector = Detector()
    # Run detection (returns a flag saying wether the signal contains an AIS, 
    # the corresponding signal block and the associated index)
    is_ais, v_block, block_index = detector.preamble_detector(
        v_signal_demodulated, C_DETECTION_THRESHOLD)

    ####################### Decoding #######################
    if is_ais:
        # Decoder object
        decoder = Decoder()
        # Decoding 
        v_ais_bits = decoder.decode(v_block)
        # Get the data
        data = decoder.get_data(v_ais_bits)
        # Print the ship's info
        print('\nRetieved data\n')
        print(f"Message Type    : {data['msg_type']}")
        print(f"MMSI            : {data['mmsi']}")
        print(f"Longitude (deg) : {data['longitude']}")
        print(f"Latitude (deg)  : {data['latitude']}")
        print(f"Course (deg)    : {data['course']}")
        print(f"CRC             : {data['crc']}\n")

