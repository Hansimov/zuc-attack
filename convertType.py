import struct
from decimal import Decimal

# What's the correct way to convert bytes to a hex string in Python 3?
#   https://stackoverflow.com/a/36149089/8328786
#   https://docs.python.org/3/library/stdtypes.html#bytes.hex

# Convert hex to float
#   https://stackoverflow.com/a/1592362/8328786
# Python使用struct处理二进制
#   https://www.cnblogs.com/gala/archive/2011/09/22/2184801.html
# Python3 Doc - struct
#   https://docs.python.org/3/library/struct.html#format-characters
def hex2float(hex_str): # 4 bytes
    float_num = struct.unpack('f',bytearray.fromhex(hex_str))[0]
    return float_num
def hex2int8(hex_str): # 1 byte
    int8_num = struct.unpack('b',bytearray.fromhex(hex_str))[0]
    return int8_num
def hex2int32(hex_str):   # 4 bytes
    int32_num = struct.unpack('i', bytearray.fromhex(hex_str))[0]
    return int32_num

def hex2dec(hex_str):
    dec_num = int(hex_str, 16)
    return dec_num

# Convert from ASCII string encoded in Hex to plain ASCII?
#   https://stackoverflow.com/a/27519487/8328786
def hex2ascii(hex_str):
    ascii_str = bytes.fromhex(hex_str).decode()
    return ascii_str
def hex2binvec(hex_str):
    pass

def hex2binstr(hex_str):
    hex_str = hex_str.upper()
    hex_len = len(hex_str)
    bin_len = 4 * hex_len
    bin_str = ''
    for i in range(0, hex_len):
        if   hex_str[i] == '0':
            bin_str += '0000'
        elif hex_str[i] == '1':
            bin_str += '0001'
        elif hex_str[i] == '2':
            bin_str += '0010'
        elif hex_str[i] == '3':
            bin_str += '0011'
        elif hex_str[i] == '4':
            bin_str += '0100'
        elif hex_str[i] == '5':
            bin_str += '0101'
        elif hex_str[i] == '6':
            bin_str += '0110'
        elif hex_str[i] == '7':
            bin_str += '0111'
        elif hex_str[i] == '8':
            bin_str += '1000'
        elif hex_str[i] == '9':
            bin_str += '1001'
        elif hex_str[i] == 'A':
            bin_str += '1010'
        elif hex_str[i] == 'B':
            bin_str += '1011'
        elif hex_str[i] == 'C':
            bin_str += '1100'
        elif hex_str[i] == 'D':
            bin_str += '1101'
        elif hex_str[i] == 'E':
            bin_str += '1110'
        elif hex_str[i] == 'F':
            bin_str += '1111'
        else:
            bin_str += '0000'
    # print(bin_str)
    return bin_str

# Display a decimal in scientific notation
#   https://stackoverflow.com/a/6913576/8328786
def floatSciNote(float_num, sig_digits):
    float_num = float(float_num)
    sci_note_fmt = '{:.' + str(sig_digits) + 'E}'
    sci_float_str = sci_note_fmt.format(float_num)
    return sci_float_str
