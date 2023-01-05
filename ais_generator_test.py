"""
==========================
AIS packets generator test
==========================

This script provides some tests on the ais_generator module. In order to check the correctness of our generator, we
take a AIVDM sentence and compare, at each step of the packet generation, the true output with the output computed by
our module. The AIVDM sentence and the true outputs are given by in the paper of Andis Dembovskis (See reference [1]
in ais_generator.py)
"""

from ais_generator import *

ais_msg = '!AIVDM,1,1,,B,19NS7Sp02wo?HETKA2K6mUM20<L=,0*27'

out1 = np.array(list(map(int, list(
    "000001001001011110100011000111100011111000000000000010111111110111001111011000010101100100011011010001000010011011000110110101100101011101000010000000001100011100001101"))))
out2 = np.array(list(map(int, list(
    "001000001110100111000101011110000111110000000000110100001011111111110011100001101001101011011000001000100110010001100011011010111110101001000010000000001110001110110000"))))
out3 = np.array(list(map(int, list(
    "0010000011101001110001010111100001111100000000001101000010111111111100111000011010011010110110000010001001100100011000110110101111101010010000100000000011100011101100001001100100100000"))))
out4 = np.array(list(map(int, list(
    "00100000111010011100010101111000011111000000000001101000010111110111110001110000110100110101101100000100010011001000110001101101011111001010010000100000000011100011101100001001100100100000"))))
out5 = np.array(list(map(int, list(
    "00000000010101010101010101010101011111100010000011101001110001010111100001111100000000000110100001011111011111000111000011010011010110110000010001001100100011000110110101111100101001000010000000001110001110110000100110010010000001111110000000000000000000000000"))))
out6 = np.array(list(map(int, list(
    "10101010110011001100110011001100111111101001010111100100001011001111101011111101010101010001101011000000111111010000101000110111001110001010110100100010010111010001110011111101100100101001010101011110100001110101101110110110101011111110101010101010101010101010"))))


def test_get_message_bit():
    assert np.array_equal(out1, get_message_bit(ais_msg))


def test_flip_bits():
    ais_bits = get_message_bit(ais_msg)
    ais_bits = flip_bits(ais_bits)
    assert np.array_equal(out2, ais_bits)


def test_add_checksum():
    ais_bits = get_message_bit(ais_msg)
    ais_bits = flip_bits(ais_bits)
    assert np.array_equal(out3, add_checksum(ais_bits))


def test_bit_stuffing():
    ais_bits = get_message_bit(ais_msg)
    ais_bits = flip_bits(ais_bits)
    ais_bits = add_checksum(ais_bits)
    assert np.array_equal(out4, bit_stuffing(ais_bits))


def test_add_preamble_flag():
    ais_bits = get_message_bit(ais_msg)
    ais_bits = flip_bits(ais_bits)
    ais_bits = add_checksum(ais_bits)
    ais_bits = bit_stuffing(ais_bits)
    assert np.array_equal(out5, add_preamble_flag(ais_bits))


def test_get_ais_packet():
    assert np.array_equal(out6, get_ais_packet(ais_msg))


def test_ais_inversion():
    ais_bits = get_message_bit(ais_msg)
    ais_packet = get_ais_packet(ais_msg)
    ais_inv = invert_ais_packet(ais_packet)

    assert np.array_equal(ais_bits, ais_inv)


def test_ais_inversion_random():
    out = True
    n_exp = 1000
    size_bits = 100

    for _ in range(n_exp):
        # Random signal
        ais_bits_init = np.random.randint(0, 2, size=size_bits)

        # Build the packet
        ais_bits = flip_bits(ais_bits_init)
        ais_bits = add_checksum(ais_bits)
        ais_bits = bit_stuffing(ais_bits)
        ais_bits = add_preamble_flag(ais_bits)
        ais_bits = nrzi(ais_bits)

        # Invert the packet
        ais_inv = invert_ais_packet(ais_bits)

        out &= np.array_equal(ais_bits_init, ais_inv)

    assert out