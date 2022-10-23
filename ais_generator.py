"""
=====================
AIS packets generator
=====================

This modules provides a function which generates an AIS packet from an AIVDM/AIVDO sentence. It implements in Python
the code given by the paper by Andis Dembovskis about AIS message extraction.

References
----------
[1] Andis Dembovskis, "AIS message extraction from overlapped AIS signals for SAT-AIS applications", Bremen University,
March 2015.
"""

import numpy as np


def get_message_bit(ais_msg):
    """Returns the AIS data bits out of the AIVDM/AIVDO sentence.

    Parameters
    ----------
    ais_msg : str
        The AIVDM/AIVDO sentence.

    Returns
    -------
    ais_data_bit : (binary) array_like
        The data bits extracted from the AIS message.
    """
    ais_data_str = ais_msg.split(',')[5]  # Crops the part corresponding to the AIS data
    ais_data_dec = np.array(list(map(ord, ais_data_str)))  # Converts each character to its ASCII integer code
    ais_data_bitstring = ''

    #  This loop performs the 6-bit formal conversion
    for i in range(len(ais_data_dec)):
        if ais_data_dec[i] < 88:
            ais_data_dec[i] -= 48
        else:
            ais_data_dec[i] -= 56

        ais_data_bitstring += bin(ais_data_dec[i]).replace('0b', '').zfill(6)  # Decimal to 6-bit representation

    ais_data_bit = np.array(list(map(int, list(ais_data_bitstring))))  # Bitstring to binary array

    return ais_data_bit


def flip_bits(ais_data_bit):
    """Flips the bits of the AIS data bits.

    Parameters
    ----------
    ais_data_bit : (binary) array_like
        The AIS data bits.
    """
    for i in range(0, ais_data_bit.size, 8):
        ais_data_bit[i:i + 8] = np.flip(ais_data_bit[i:i + 8])


def add_checksum(ais_data_bit):
    """Adds the checksum at the end of the message, by using the CRC-16-CCITT standard.

    Parameters
    ----------
    ais_data_bit : (binary) array_like
        The AIS data bits.

    Returns
    -------
    ais_data_bit : (binary) array_like
        The AIS data bits with the checksum at the end of the message.
    """

    # Parameters
    crc_width = 16
    poly = np.array(list(map(int, bin(2 ** 16 + 2 ** 12 + 2 ** 5 + 2 ** 0).replace('0b', ''))))
    init_val = np.ones(crc_width)
    final_xor = np.ones(crc_width)

    # Registry initialization
    am = np.concatenate((ais_data_bit, np.zeros(crc_width)))

    am[:crc_width] = np.logical_xor(am[0:crc_width], init_val)

    # CRC calculation
    reg = np.concatenate((np.array([0]), am[:crc_width]))
    for i in range(crc_width, am.size):
        reg = np.concatenate((reg[1:], np.array([am[i]])))
        if reg[0] == 1:
            reg = np.logical_xor(reg, poly)
    mcrc = np.logical_xor(reg[1:], final_xor)

    ais_data_bit = np.concatenate((ais_data_bit, mcrc))

    return ais_data_bit


def bit_stuffing(ais_data_bit):
    """Performs bit-stuffing to the AIS data bits.

    Bit-stuffing means that 0 is added after every five consecutive 1.

    Parameters
    ----------
    ais_data_bit : (binary) array_like
        The AIS data bits.

    Returns
    -------
    ais_data_bit : (binary) array_like
        The AIS data bits after the bit-stuffing.
    """
    n_consecutive = 5
    i = n_consecutive - 1

    while i <= ais_data_bit.size:
        if np.array_equal(ais_data_bit[i - (n_consecutive - 1):i + 1], np.ones(n_consecutive)):
            ais_data_bit = np.concatenate((ais_data_bit[:i + 1], np.array([0]), ais_data_bit[i + 1:]))
            i += n_consecutive
        else:
            i += 1

    return ais_data_bit


def add_preamble_flag(ais_data_bit):
    """Builds the AIS packet.

    The resulting AIS packet contains in this order :
        1) Ramp-Up bits,
        2) Preamble bits,
        3) The start flag,
        4) The AIS data bits,
        5) The end flag,
        6) Buffer.

    Parameters
    ----------
    ais_data_bit : (binary) array_like
        The AIS data bits.

    Returns
    -------
    ais_data_bits : (binary) array_like
        The built AIS packet.
    """
    preamble = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])
    ais_data_bit = np.concatenate((np.zeros(8), preamble, flag, ais_data_bit, flag, np.zeros(24)))

    return ais_data_bit


def non_return_to_zero_inversion(ais_data_bit):
    """Performs the non-return to zero inversion to the AIS packet.

    Parameters
    ----------
    ais_data_bit : (binary) array_like
        The AIS data bits.

    Returns
    -------
    ais_data_bit : (binary) array_like
        The AIS packet after the non-return to zero inversion.
    """
    bin_msg = np.copy(ais_data_bit)
    inv_case = 0  # invert when 0 is observed

    volt_state = 0  # voltage state, assume initial = 0
    for i in range(bin_msg.size):
        if bin_msg[i] != inv_case:
            bin_msg[i] = volt_state
        else:
            if volt_state == 0:
                volt_state = 1
            else:
                volt_state = 0
            bin_msg[i] = volt_state
    ais_data_bit = np.copy(bin_msg)

    return ais_data_bit


def get_ais_packet(ais_msg):
    """Return the AIS packet from the AIS message.

    Parameters
    ----------
    ais_msg : str
        The The AIVDM/AIVDO sentence associated to the AIS message.

    Returns
    -------
    ais_data_bit : (binary) array_like
        The AIS packet.
    """
    ais_data_bit = get_message_bit(ais_msg)
    flip_bits(ais_data_bit)
    ais_data_bit = add_checksum(ais_data_bit)
    ais_data_bit = bit_stuffing(ais_data_bit)
    ais_data_bit = add_preamble_flag(ais_data_bit)
    ais_data_bit = non_return_to_zero_inversion(ais_data_bit).astype(int)

    return ais_data_bit
