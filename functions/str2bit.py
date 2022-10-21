def signalFromName(name):

    byte_array = (name).encode('latin-1')
    binary_int = int.from_bytes(byte_array, "big")
    binary_string = bin(binary_int)
    binary_string = binary_string[2:].zfill(len(binary_string))

    return [int(i) for i in binary_string]


def nameFromSignal(signal):

    string = ''

    for i in signal :
        string += str(i)

    binary_int = int(string, 2)
    byte_number = binary_int.bit_length() + 7 // 8

    binary_array = binary_int.to_bytes(byte_number, "big")
    ascii_text = binary_array.decode('latin-1')

    return ascii_text
