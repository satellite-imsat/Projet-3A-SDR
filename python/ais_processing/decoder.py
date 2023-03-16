#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   decoder.py
@Time    :   2023/03/15 12:21:16
@Author  :   Selman Sezgin 
@Version :   1.0
@Contact :   selman.sezgin@imt-atlantique.net
@License :   (C)Copyright 2023, Selman Sezgin
@Desc    :   This class provides a function to retrieve ship characteritics from
             an AIS message (type 1)
'''

import numpy as np

class Decoder:

    """
    ==============================
        AIS packets decoder
    ==============================

    This class provides a function to retrieve ship characteritics from
    an AIS message (type 1). It implements in Python the code given by the paper 
    by Andis Dembovskis about AIS message extraction.

    References
    ----------
    [1] Andis Dembovskis, "AIS message extraction from overlapped AIS signals 
    for SAT-AIS applications", Bremen University,
    March 2015.
    """

    def __init__(self) -> None:
        pass
   

    def flip_bits(self,v_ais_bits : np.ndarray) -> np.ndarray:
        """Flips the bits of the AIS data bits.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_flipped: array-like
            The flipped version of the AIS data bits.
        """
        n = v_ais_bits.size
        v_ais_bits_flipped = np.zeros(n-(n%8))

        for i in range(0, n-(n%8), 8):
            v_ais_bits_flipped[i:i + 8] = np.flip(v_ais_bits[i:i + 8])

        return v_ais_bits_flipped

    def nrzi_inv(self, v_ais_bits : np.ndarray) -> np.ndarray:
        """Invert the non return to zero inversion.

        Parameters
        ----------
        v_ais_bits: array-like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_inv: array-like
            The AIS data bits without non return to zero inversion.
        """
        n = np.size(v_ais_bits)
        v_ais_bits_inv = np.zeros(n)
        state = 0

        for i in range(n):
            if v_ais_bits[i] != state:
                v_ais_bits_inv[i] = 0
                state = v_ais_bits[i]
            else:
                v_ais_bits_inv[i] = 1

        return v_ais_bits_inv


    def bit_stuffing_inv(self, v_ais_bits : np.ndarray) -> np.ndarray :
        """Invert the bits stuffing.
    
        Parameters
        ----------
        v_ais_bits: array-like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_wo_bit_stuffing: array-like
            The AIS data bits without bit stuffing.
        """
        n_cons = 5
        i = n_cons - 1
        i0 = 0
        v_ais_bits_wo_bit_stuffing = np.array([])
        n = v_ais_bits.size

        while i < n:
            if np.array_equal(v_ais_bits[i - (n_cons - 1):i + 1], np.ones(n_cons)):
                v_ais_bits_wo_bit_stuffing = np.concatenate((v_ais_bits_wo_bit_stuffing, v_ais_bits[i0:i+1]))
                i0 = i + 2
                i += n_cons + 1
            else:
                i += 1

        v_ais_bits_wo_bit_stuffing = np.concatenate((v_ais_bits_wo_bit_stuffing, v_ais_bits[i0:]))

        return v_ais_bits_wo_bit_stuffing

    def remove_preamble_flag(self,v_ais_bits : np.ndarray) -> np.ndarray:
        """Remove the preamble and the start/end flags from the AIS packet.

        Parameters
        ----------
        v_ais_bits: array-like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_wo_preamble_flags: array-like
            The AIS packet without the preamble and the start/end flags.
        """
        return np.copy(v_ais_bits[40:-32])
    
    def compute_crc(self, v_ais_bits : np.ndarray) -> np.ndarray :
        """Computes the checksum of the message, by using 
        the CRC-16-CCITT standard.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits

        Returns
        -------
        checksum: array_like
            The computed checksum
        """
        # Parameters
        crc_width = 16
        poly = np.array(
            list(map(int, bin(2**16 + 2**12 + 2**5 + 2**0).replace('0b', '')))
            )
        init_val = np.ones(crc_width)
        final_xor = np.ones(crc_width)

        # Registry initialization
        am = np.concatenate((v_ais_bits, np.zeros(crc_width)))
        am[:crc_width] = np.logical_xor(am[0:crc_width], init_val)

        # CRC calculation
        reg = np.concatenate((np.array([0]), am[:crc_width]))
        for i in range(crc_width, am.size):
            reg = np.concatenate((reg[1:], np.array([am[i]])))
            if reg[0] == 1:
                reg = np.logical_xor(reg, poly)
        checksum = np.logical_xor(reg[1:], final_xor)

        return checksum


    def remove_checksum(self,v_ais_bits : np.ndarray) -> np.ndarray:
        """Remove the checksum from the AIS data bits. Also computes the 
        signal CRC and compare it to the transmitted one.

        Parameters
        ----------
        v_ais_bits: array-like
            The AIS data bits

        Returns
        -------
        v_ais_bits_wo_checksum: array-like
            The AIS data bits without the checksum
        """

        crc_width = 16
        # Get the checksum
        checksum = v_ais_bits[-crc_width:]
        # Get the vector without the checksum
        v_ais_bits_wo_checksum = np.copy(v_ais_bits[:-crc_width])
        # Compute the checksum
        vector_checksum = self.compute_crc(v_ais_bits_wo_checksum)

        # Check that the computed CRC matches the computed one 
        self.correct_checksum = True
        if np.linalg.norm(vector_checksum - checksum) > 1e-7 :
               self.correct_checksum = False

        return v_ais_bits_wo_checksum

    

    def twos_comp(self, val, size):
        """
        """
        if (val & (1 << (size - 1))) != 0: 
            val = val - (1 << size)
        return val
    
    def bin_array_to_dec(self,x, is_signed):
        """
        """
        return self.twos_comp(int(''.join(list(map(str, x.astype("int")))), 2), len(x))\
            if is_signed else int(''.join(list(map(str, x.astype("int")))), 2)

    def get_msg_type(self,v_ais_bits : np.ndarray) -> float :
        """Returns the message type from an AIS message.

        Paramters
        ---------
        v_ais_bits: array-like
            the ais bits vector

        Returns
        -------

        msg_type: float
            the AIS message type
        """

        msg_type = self.bin_array_to_dec(v_ais_bits[:6], is_signed = False)
        return msg_type

    def get_mmsi(self,v_ais_bits : np.ndarray) -> float :
        """Returns the MMSI from an AIS message.

        Paramters
        ---------
        v_ais_bits: array-like
            the ais bits vector

        Returns
        -------

        mmsi: float
            the ship's MMSI
        """

        mmsi = self.bin_array_to_dec(v_ais_bits[8:38], is_signed = False)
    
        return mmsi
    
    def get_lat(self,v_ais_bits : np.ndarray) -> float :
        """Returns the latitude in degrees from an AIS message.

        Paramters
        ---------
        v_ais_bits: array-like
            the ais bits vector

        Returns
        -------

        latitude_deg: float
            the ship's latitude in degrees
        """
        latitude_deg = self.bin_array_to_dec(v_ais_bits[89:116], is_signed = True) / 10000 / 60
        return latitude_deg

    def get_long(self,v_ais_bits : np.ndarray) -> float :
        """Returns the longitude in degrees from an AIS message.

        Paramters
        ---------
        v_ais_bits: array-like
            the ais bits vector

        Returns
        -------

        longitude_deg: float
            the ship's longitude in degrees
        """
        longitude_deg = self.bin_array_to_dec(v_ais_bits[61:89], is_signed = True) / 10000 / 60 
        return longitude_deg
    
    def get_course(self,v_ais_bits : np.ndarray) -> float :
        """Returns the course in degrees from an AIS message.

        Paramters
        ---------
        v_ais_bits: array-like
            the ais bits vector

        Returns
        -------

        course_deg: float
            the ship's course in degrees
        """

        course_deg = self.bin_array_to_dec(v_ais_bits[116:128], is_signed = False) / 10 
       
        return course_deg
    
    def decode(self, v_ais_bits : np.ndarray) -> np.ndarray :
        """Process the AIS packet to retrieve the initial AIS data bits. 
        The NRZI inversion is supposed to have been run before this function.

        Parameters
        ----------
        ais_bits: array-like
            The AIS data bits.

        Returns
        -------
        ais_bits: array-like
            The initial AIS data bits.
        """

        # Remove preamble and flags
        v_ais_bits = self.remove_preamble_flag(v_ais_bits = v_ais_bits)
        # Invert bit stuffing
        v_ais_bits = self.bit_stuffing_inv(v_ais_bits = v_ais_bits)
        # Remove the checksum (and check its correctness)
        v_ais_bits = self.remove_checksum(v_ais_bits = v_ais_bits)
        # Flip the bits
        v_ais_bits = self.flip_bits(v_ais_bits = v_ais_bits)

        return v_ais_bits

    def get_data(self,v_ais_bits : np.ndarray) -> dict :

        """Given the decode AIS bits, this function extracts the following
        characteristics and stores them in a dictionary:
        - msg_type <-> The type of the message
        - mmsi <-> The ship's idendity 
        - latitude <-> The latitude in degrees
        - longitude <-> The longitude in degrees
        - course <-> The course in degrees
        - crc <-> Correct or not correct CRC

        The longitude, latitude and course are stored with 6 digits.

        Parameters
        ----------

        v_ais_bits: array-like
            the decoded ais bits
        
        Returns
        -------

        data: dict
            A dictionary containing the signal data
        """
        data = {}
        data['msg_type'] = self.get_msg_type(v_ais_bits)
        data['mmsi'] = self.get_mmsi(v_ais_bits)
        data['latitude'] = round(self.get_lat(v_ais_bits), ndigits = 6)
        data['longitude'] = round(self.get_long(v_ais_bits), ndigits = 6)
        data['course'] = round(self.get_course(v_ais_bits), ndigits = 6)
        data['crc'] = "correct" if self.correct_checksum else "not correct" 
        

        return data








