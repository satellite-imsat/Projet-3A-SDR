#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   app.py
@Time    :   2023/03/14 22:20:28
@Author  :   Thomas Aussaguès & Selman Sezgin
@Version :   1.0
@Contact :   {name.surname}@imt-atlantique.net
@License :   (C)Copyright 2023, Thomas Aussaguès & Selman Sezgin
@Desc    :   A script to illustrate the proposed architecture for processing
             AIS signals on real data.
'''

"""
This script test the proposed architecture on real AIS data that was recorded
in Bretagne (Île de Ouessant) with a sampling frequnecy of 125/4 kHz. 
Two signals are included : exOutBurst34.txt and exOutBurst7.txt. 
Corresponding ship characteristics are given below.

----------------------------- Signals description -----------------------------
exOutBurst34.txt
----------------
Message ID : 1
MMSI : 305323000
Longitude : -6.233335e+00° (>0 = East, <0=West)
Latitude : 4.799603e+01° (>0 = North, <0 = South)
Course over ground : 2.530000e+01

exOutBurst7.txt (=> Unfortunaly not working...)
---------------
Message ID : 1
MMSI : 357842000
Longitude : -6.172383e+00° (>0 = East, <0=West)
Latitude : 4.843545e+01° (>0 = North, <0 = South)
Course over ground : 2.081000e+02
"""

# Imports
from ais_processing.demodulator import Demodulator
from ais_processing.detector import Detector
from ais_processing.decoder import Decoder
import numpy as np
# To resample signals
from scipy.signal import resample

# Path to the recorded signal (a txt file that contains two columns : one with I
# and the other with Q component). The signal was recorded using a sampling
# frequency of 125/4 kHz. By default, ais files are stored in the folder ais_data.
path = "python/ais_data/exOutBurst34.txt"

# Threshold for the detection. Set to 32 => 0 error on the preamble + start flag
# sequence
C_DETECTION_THRESHOLD = 32


if __name__ == '__main__':

    print("\n**** AIS processing example on real data ****\n")
 
    ##################### Signal loading #####################
    # Load signal
    v_signal_rx = np.loadtxt(path, delimiter=" ")
    # Get I and Q component and sum them to obtain I + jQ
    v_signal_rx = v_signal_rx[:, 0] +1j * v_signal_rx[:, 1]

    ##################### Signal preprocessing #############
    # Signal resampling: the sampling frequency goes from 125/4 kHz
    # to 9600 kHz (upsampling factor = 1000 w.r.t to the base 
    # sampling frequency of 9.6 kHz)
    v_signal_rx = resample(v_signal_rx, 
                           num = int(v_signal_rx.shape[0] * 4 * 8 * 9.6 / 10))


    ##################### Demodulator #####################
    demodulator = Demodulator()
    v_signal_demodulated = demodulator.demod_signal_gmsk(
        v_signal_rx = v_signal_rx, up_sampling_factor=100)

    
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
        print('Retieved data\n')
        print(f"Message Type    : {data['msg_type']}")
        print(f"MMSI            : {data['mmsi']}")
        print(f"Longitude (deg) : {data['longitude']}")
        print(f"Latitude (deg)  : {data['latitude']}")
        print(f"Course (deg)    : {data['course']}")
        print(f"CRC             : {data['crc']}\n")

    

    



