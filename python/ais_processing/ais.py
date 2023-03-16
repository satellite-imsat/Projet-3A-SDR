#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   ais.py
@Time    :   2023/03/15 12:18:59
@Author  :   Selman Sezgin 
@Version :   1.0
@Contact :   selman.sezgin@imt-atlantique.net
@License :   (C)Copyright 2023, Selman Sezgin
@Desc    :   This class provides a function which generates an AIS packet from an 
             AIVDM/AIVDO sentence
'''


import numpy as np
from pyais.encode import encode_msg
from pyais.messages import MessageType1

class GenAIS:

    """
    ==============================
        AIS packets generator
    ==============================

    This class provides a function which generates an AIS packet from an 
    AIVDM/AIVDO sentence. It implements in Python the code given by the paper 
    by Andis Dembovskis about AIS message extraction.

    References
    ----------
    [1] Andis Dembovskis, "AIS message extraction from overlapped AIS signals 
    for SAT-AIS applications", Bremen University,
    March 2015.
    [2]  Leon Morten Richter (15 March 2023), PyAIS python package, 
    https://pypi.org/project/pyais/
    """

    def __init__(self) -> None:
        pass

    def get_message_bit(self, ais_msg : str) -> np.ndarray :

        """Returns the AIS data bits out of the AIVDM/AIVDO sentence.

        Parameters
        ----------
        ais_msg: str
            The AIVDM/AIVDO sentence.

        Returns
        -------
        v_v_ais_bits: array_like
            The data bits extracted from the AIS message.
        """

        # Crops the part corresponding to the AIS data
        ais_data_str = ais_msg.split(',')[5]  
        # Converts each character to its ASCII integer code
        ais_data_dec = np.array(list(map(ord, ais_data_str)))  
        v_ais_bitsstring = ''

        #  This loop performs the 6-bit formal conversion
        for i in range(len(ais_data_dec)):
            if ais_data_dec[i] < 88:
                ais_data_dec[i] -= 48
            else:
                ais_data_dec[i] -= 56
            # Decimal to 6-bit representation
            v_ais_bitsstring += bin(ais_data_dec[i]).replace('0b', '').zfill(6)  
        # Bitstring to binary array
        v_ais_bits = np.array(list(map(int, list(v_ais_bitsstring))))  

        return v_ais_bits


    def flip_bits(self, v_ais_bits : np.ndarray) -> np.ndarray :

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
        
        v_ais_bits_flipped = np.zeros_like(v_ais_bits)

        for i in range(0, v_ais_bits.shape[0], 8):
            v_ais_bits_flipped[i:i + 8] = np.flip(v_ais_bits[i:i + 8])

        return v_ais_bits_flipped


    def compute_crc(self, v_ais_bits : np.ndarray) -> np.ndarray :

        """Computes the checksum of the message, by using 
        the CRC-16-CCITT standard.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

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


    def add_checksum(self, v_ais_bits : np.ndarray) -> np.ndarray :

        """Adds the checksum at the end of the message, 
        by using the CRC-16-CCITT standard.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

        Returns
        -------
        v_ais_bits_crc: array_like
            The AIS data bits with the checksum at the end of the message.
        """

        # Get the CRC
        crc = self.compute_crc(v_ais_bits=v_ais_bits)
        # Add the CRC
        v_ais_bits_crc = np.concatenate((v_ais_bits, crc))

        return v_ais_bits_crc


    def bit_stuffing(self, v_ais_bits : np.ndarray) -> np.ndarray :

        """Performs bit-stuffing to the AIS data bits.

        Bit-stuffing means that 0 is added after every five consecutive 1.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

        Returns
        -------
        v_ais_bits: array_like
            The AIS data bits after the bit-stuffing.
        """
        n_consecutive = 5
        i = n_consecutive - 1

        while i <= v_ais_bits.size:
            if (np.array_equal(v_ais_bits[i - (n_consecutive - 1):i + 1], 
                               np.ones(n_consecutive))):
                v_ais_bits = np.concatenate(
                    (v_ais_bits[:i + 1], np.array([0]), v_ais_bits[i + 1:])
                    )
                i += n_consecutive
            else:
                i += 1

        return v_ais_bits


    def add_preamble_flag(self, v_ais_bits : np.ndarray) -> np.ndarray :

        """Builds the AIS packet.

        The resulting AIS packet contains in this order :
            1) Ramp-Up bits (8 bits),
            2) Preamble bits (24 bits),
            3) The start flag (8 bits),
            4) The AIS data bits,
            5) The end flag,
            6) Buffer.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

        Returns
        -------
        out: array_like
            The built AIS packet.
        """
        
        # Preamble
        preamble = np.array(
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 
             0, 1, 0, 1, 0, 1, 0, 1]
             )
        # Start flag
        flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])
        # Concatenate the rampu-up bits, the preamble and flags with the AIS 
        # bits
        out = np.concatenate(
            (np.zeros(8), preamble, flag, v_ais_bits, flag, np.zeros(24))
            )

        return out


    def nrzi(self, v_ais_bits : np.ndarray) -> np.ndarray :

        """Performs the non-return to zero inversion to the AIS packet.

        Parameters
        ----------
        v_ais_bits: array_like
            The AIS data bits.

        Returns
        -------
        out: array_like
            The AIS packet after the non-return to zero inversion.
        """
        out = np.copy(v_ais_bits)
        inv_case = 0  # invert when 0 is observed

        volt_state = 0  # voltage state, assume initial = 0
        for i in range(out.size):
            if out[i] != inv_case:
                out[i] = volt_state
            else:
                if volt_state == 0:
                    volt_state = 1
                else:
                    volt_state = 0
                out[i] = volt_state

        return out


    def get_ais_packet(self, ais_msg : str) -> np.ndarray :
        
        """Return the AIS packet from the AIS message.

        Parameters
        ----------
        ais_msg: str
            The The AIVDM/AIVDO sentence associated to the AIS message.

        Returns
        -------
        v_ais_bits: array_like
            The AIS packet.
        """
        v_ais_bits = self.get_message_bit(ais_msg)
        v_ais_bits = self.flip_bits(v_ais_bits)
        v_ais_bits = self.add_checksum(v_ais_bits)
        v_ais_bits = self.bit_stuffing(v_ais_bits)
        v_ais_bits = self.add_preamble_flag(v_ais_bits)
        v_ais_bits = self.nrzi(v_ais_bits)

        return v_ais_bits


    def get_ais_ref(self):

        """Returns the 24 preambule bits and the 8 bits
        start flag (with NRZI coding) used as a reference 
        for signal detection.

        Returns
        -------

        v_ais_bits: array_like
            The AIS reference bits.
        
        """

        # 24 bits preambule
        preamble = np.array(
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 
                0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
                )
    
        # 8 bits start flag
        flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])
        # Contenation with 8 ramp up bits
        v_ais_bits = np.concatenate((preamble, flag))
        # NRZI
        v_ais_bits = self.nrzi(v_ais_bits=preamble)

        return  v_ais_bits

    def gen_rand_ais_type_1(self, course_deg = None, lat_deg = None, 
                            lon_deg = None, mmsi = None, 
                            return_info = False) -> str :

        """Generates the AIS packet associated to the type I message 
        corresponding to the given parameters. If no parameters are provided, 
        then random course, latitude, longitude ans MMSI are used.
        
        Parameters
        ----------

        course_deg: float between 0 and 360 with 1 digits
                the boat course in degrees
        lat_deg: float between - 90 and 90 with 3 digits
                the boat latitude in degrees
        lon_deg: float between - 180 and 180 with 3 digits
                the boat longitude in degrees
        mmsi: int between 0 and 1e10 - 1
                the boat Maritime Mobile Service Identity
        return_info: bool
                whether to return the data (MMSI, longitude, latitude, 
                and course)or not
        
        Returns
        -------

        ais_packet : (binary) array-like
            the ais packet corresponding to the given parameters
        mmsi, lat_deg, lon_deg, course_deg : dict of floats
            the transmitted data
        
        """

        # Get random course, latitude, longitude and MMSI

        if course_deg is None : 
            course_deg = np.round(360 * np.random.ranf(), decimals = 1)
        if lat_deg is None :
            lat_deg = np.round(180 * np.random.ranf() - 90, decimals = 3)
        if lon_deg is None :
            lon_deg = np.round(360 * np.random.ranf() - 180, decimals = 3)
        if mmsi is None :
            mmsi = str(np.random.randint(low = 0, high = 1e8))

        # The AIVDM/AIVDO sentence associated to the AIS message.
        ais_msg = MessageType1.create(course = course_deg, lat = lat_deg, 
                                      lon = lon_deg, mmsi = mmsi)
        
        # Conversion to a binary message
        ais_msg_encoded = encode_msg(msg = ais_msg)

        # Packet creation : 1) Ramp-Up bits, 2) Preamble bits, 3) The start flag, 
        # 4) The AIS data bits, 5) The end flag, 6) Buffer.
        ais_packet = self.get_ais_packet(ais_msg = ais_msg_encoded[0])

        # Return the packet and the data
        if return_info :
            return ais_packet, {"msg_type" : 1, "mmsi" : mmsi, "longitude" : lon_deg, 
                                "latitude" : lat_deg, "course" : course_deg}

        # Return only the packet
        return ais_packet


