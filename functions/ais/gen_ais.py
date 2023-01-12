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
    ais_msg: str
        The AIVDM/AIVDO sentence.

    Returns
    -------
    ais_bits: array_like
        The data bits extracted from the AIS message.
    """
    ais_data_str = ais_msg.split(',')[5]  # Crops the part corresponding to the AIS data
    ais_data_dec = np.array(list(map(ord, ais_data_str)))  # Converts each character to its ASCII integer code
    ais_bitsstring = ''

    #  This loop performs the 6-bit formal conversion
    for i in range(len(ais_data_dec)):
        if ais_data_dec[i] < 88:
            ais_data_dec[i] -= 48
        else:
            ais_data_dec[i] -= 56

        ais_bitsstring += bin(ais_data_dec[i]).replace('0b', '').zfill(6)  # Decimal to 6-bit representation

    ais_bits = np.array(list(map(int, list(ais_bitsstring))))  # Bitstring to binary array

    return ais_bits


def flip_bits(ais_bits):
    """Flips the bits of the AIS data bits.

    Parameters
    ----------
    ais_bits: array_like
        The AIS data bits.

    Returns
    -------
    out: array-like
        The flipped version of the AIS data bits.
    """
    n = ais_bits.size
    out = np.zeros(n)

    for i in range(0, n, 8):
        out[i:i + 8] = np.flip(ais_bits[i:i + 8])

    return out


def add_checksum(ais_bits):
    """Adds the checksum at the end of the message, by using the CRC-16-CCITT standard.

    Parameters
    ----------
    ais_bits: array_like
        The AIS data bits.

    Returns
    -------
    out: array_like
        The AIS data bits with the checksum at the end of the message.
    """
    # Parameters
    crc_width = 16
    poly = np.array(list(map(int, bin(2**16 + 2**12 + 2**5 + 2**0).replace('0b', ''))))
    init_val = np.ones(crc_width)
    final_xor = np.ones(crc_width)

    # Registry initialization
    am = np.concatenate((ais_bits, np.zeros(crc_width)))
    am[:crc_width] = np.logical_xor(am[0:crc_width], init_val)

    # CRC calculation
    reg = np.concatenate((np.array([0]), am[:crc_width]))
    for i in range(crc_width, am.size):
        reg = np.concatenate((reg[1:], np.array([am[i]])))
        if reg[0] == 1:
            reg = np.logical_xor(reg, poly)
    mcrc = np.logical_xor(reg[1:], final_xor)

    out = np.concatenate((ais_bits, mcrc))

    return out


def bit_stuffing(ais_bits):
    """Performs bit-stuffing to the AIS data bits.

    Bit-stuffing means that 0 is added after every five consecutive 1.

    Parameters
    ----------
    ais_bits: array_like
        The AIS data bits.

    Returns
    -------
    ais_bits: array_like
        The AIS data bits after the bit-stuffing.
    """
    n_consecutive = 5
    i = n_consecutive - 1

    while i <= ais_bits.size:
        if np.array_equal(ais_bits[i - (n_consecutive - 1):i + 1], np.ones(n_consecutive)):
            ais_bits = np.concatenate((ais_bits[:i + 1], np.array([0]), ais_bits[i + 1:]))
            i += n_consecutive
        else:
            i += 1

    return ais_bits


def add_preamble_flag(ais_bits):
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
    ais_bits: array_like
        The AIS data bits.

    Returns
    -------
    out: array_like
        The built AIS packet.
    """
    preamble = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    flag = np.array([0, 1, 1, 1, 1, 1, 1, 0])
    out = np.concatenate((np.zeros(8), preamble, flag, ais_bits, flag, np.zeros(24)))

    return out


def nrzi(ais_bits):
    """Performs the non-return to zero inversion to the AIS packet.

    Parameters
    ----------
    ais_bits: array_like
        The AIS data bits.

    Returns
    -------
    out: array_like
        The AIS packet after the non-return to zero inversion.
    """
    out = np.copy(ais_bits)
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


def get_ais_packet(ais_msg):
    """Return the AIS packet from the AIS message.

    Parameters
    ----------
    ais_msg: str
        The The AIVDM/AIVDO sentence associated to the AIS message.

    Returns
    -------
    ais_bits: array_like
        The AIS packet.
    """
    ais_bits = get_message_bit(ais_msg)
    ais_bits = flip_bits(ais_bits)
    ais_bits = add_checksum(ais_bits)
    ais_bits = bit_stuffing(ais_bits)
    ais_bits = add_preamble_flag(ais_bits)
    ais_bits = nrzi(ais_bits)

    return ais_bits


def nrzi_inv(ais_bits):
    """Invert the non return to zero inversion.

    Parameters
    ----------
    ais_bits: array-like
        The AIS data bits.

    Returns
    -------
    out: array-like
        The AIS data bits without non return to zero inversion.
    """
    n = np.size(ais_bits)
    out = np.zeros(n)
    state = 0

    for i in range(n):
        if ais_bits[i] != state:
            out[i] = 0
            state = ais_bits[i]
        else:
            out[i] = 1

    return out


def remove_preamble_flag(ais_bits):
    """Remove the preamble and the start/end flags from the AIS packet.

    Parameters
    ----------
    ais_bits: array-like
        The AIS data bits.

    Returns
    -------
    out: array-like
        The AIS packet without the preamble and the start/end flags.
    """
    out = np.copy(ais_bits[40:-32])
    return out


def bit_stuffing_inv(ais_bits):
    """Invert the bits stuffing.
    
    Parameters
    ----------
    ais_bits: array-like
        The AIS data bits.

    Returns
    -------
    out: array-like
        The AIS data bits without bit stuffing.
    """
    n_cons = 5
    i = n_cons - 1
    i0 = 0
    out = np.array([])
    n = ais_bits.size

    while i < n:
        if np.array_equal(ais_bits[i - (n_cons - 1):i + 1], np.ones(n_cons)):
            out = np.concatenate((out, ais_bits[i0:i+1]))
            i0 = i + 2
            i += n_cons + 1
        else:
            i += 1

    out = np.concatenate((out, ais_bits[i0:]))

    return out


def remove_checksum(ais_bits):
    """Remove the checksum from the AIS data bits.

    Parameters
    ----------
    ais_bits: array-like
        The AIS data bits.

    Returns
    -------
    out: array-like
        The AIS data bits without the checksum.
    """
    crc_width = 16
    out = np.copy(ais_bits[:-crc_width])

    return out


def invert_ais_packet(ais_bits):
    """Process the AIS packet to retrieve the initial AIS data bits.

    Parameters
    ----------
    ais_bits: array-like
        The AIS data bits.

    Returns
    -------
    ais_bits: array-like
        The initial AIS data bits.
    """
    ais_bits = nrzi_inv(ais_bits)
    ais_bits = remove_preamble_flag(ais_bits)
    ais_bits = bit_stuffing_inv(ais_bits)
    ais_bits = remove_checksum(ais_bits)
    ais_bits = flip_bits(ais_bits)

    return ais_bits


def gen_rand_ais_type_1(course_deg = None, lat_deg = None, lon_deg = None, mmsi = None) -> str :

    """Generates the AIS packet associated to the type I message corresponding to the
    given parameters. if no parameters are provided, then random course, latitude, 
    longitude ans MMSI are used.
    
    Parameters
    ----------

    - course_deg : float between 0 and 360 with 1 digits
            the boat course in degrees
    - lat_deg : float between - 90 and 90 with 3 digits
            the boat latitude in degrees
    - lat_deg : float between - 180 and 180 with 3 digits
            the boat longitude in degrees
    - mmsi : int between 0 and 1e10 - 1
            the boat Maritime Mobile Service Identity
    
    Returns
    -------

    - ais_packet : (binary) array-like
        the ais packet corresponding to the given parameters
    
    """

    # Get random course, latitude, longitude and MMSI

    if course_deg is None : 
        course_deg = np.round(360 * np.random.ranf(), decimals = 1)
    if lat_deg is None :
        lat_deg = np.round(180 * np.random.ranf() - 90, decimals = 3)
    if lon_deg is None :
        lon_deg = np.round(360 * np.random.ranf() - 180, decimals = 3)
    if mmsi is None :
        mmsi = str(np.random.randint(low = 0, high = 1e10))

    # The AIVDM/AIVDO sentence associated to the AIS message.
    ais_msg = MessageType1.create(course = course_deg, lat = lat_deg, lon = lon_deg, mmsi = mmsi)
    
    # Conversion to a binary message
    ais_msg_encoded = encode_msg(msg = ais_msg)

    # Packet creation : 1) Ramp-Up bits, 2) Preamble bits, 3) The start flag, 
    # 4) The AIS data bits, 5) The end flag, 6) Buffer.
    ais_packet = get_ais_packet(ais_msg = ais_msg_encoded[0])

    return ais_packet
