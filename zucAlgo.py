import struct
import sys
from convertType import *
from binaryOperation import *

k_hex = [''] * 16
v_hex = [''] * 16
k = [''] * 16 # initial key     -  8 bit x 16
v = [''] * 16 # initial vector  -  8 bit x 16
d = [''] * 16 # constant data   - 15 bit x 16
s = [[0]*31 for _ in range(17)] # combined bit list - 31 bit x 16+1 (The last is used to update)
r1 = [0] * 32 # register 1 - 32 bit
r2 = [0] * 32 # register 2 - 32 bit
x = [[0]*32 for _ in range(4)] # list - 32 bit x 4
w = [0] * 32 # var in nonLinearFucntion(), used by zucInit()
d = [ '100010011010111', '010011010111100', '110001001101011', '001001101011110',
      '101011110001001', '011010111100010', '111000100110101', '000100110101111',
      '100110101111000', '010111100010011', '110101111000100', '001101011110001',
      '101111000100110', '011110001001101', '111100010011010', '100011110101100']

def sboxOfZuc(list_in):
    sbox = [[]] * 4
    sbox[0] = [
        ['3E', '72', '5B', '47', 'CA', 'E0', '00', '33', '04', 'D1', '54', '98', '09', 'B9', '6D', 'CB'], 
        ['7B', '1B', 'F9', '32', 'AF', '9D', '6A', 'A5', 'B8', '2D', 'FC', '1D', '08', '53', '03', '90'],
        ['4D', '4E', '84', '99', 'E4', 'CE', 'D9', '91', 'DD', 'B6', '85', '48', '8B', '29', '6E', 'AC'], 
        ['CD', 'C1', 'F8', '1E', '73', '43', '69', 'C6', 'B5', 'BD', 'FD', '39', '63', '20', 'D4', '38'],
        ['76', '7D', 'B2', 'A7', 'CF', 'ED', '57', 'C5', 'F3', '2C', 'BB', '14', '21', '06', '55', '9B'],
        ['E3', 'EF', '5E', '31', '4F', '7F', '5A', 'A4', '0D', '82', '51', '49', '5F', 'BA', '58', '1C'], 
        ['4A', '16', 'D5', '17', 'A8', '92', '24', '1F', '8C', 'FF', 'D8', 'AE', '2E', '01', 'D3', 'AD'], 
        ['3B', '4B', 'DA', '46', 'EB', 'C9', 'DE', '9A', '8F', '87', 'D7', '3A', '80', '6F', '2F', 'C8'], 
        ['B1', 'B4', '37', 'F7', '0A', '22', '13', '28', '7C', 'CC', '3C', '89', 'C7', 'C3', '96', '56'],
        ['07', 'BF', '7E', 'F0', '0B', '2B', '97', '52', '35', '41', '79', '61', 'A6', '4C', '10', 'FE'],
        ['BC', '26', '95', '88', '8A', 'B0', 'A3', 'FB', 'C0', '18', '94', 'F2', 'E1', 'E5', 'E9', '5D'],
        ['D0', 'DC', '11', '66', '64', '5C', 'EC', '59', '42', '75', '12', 'F5', '74', '9C', 'AA', '23'],
        ['0E', '86', 'AB', 'BE', '2A', '02', 'E7', '67', 'E6', '44', 'A2', '6C', 'C2', '93', '9F', 'F1'],
        ['F6', 'FA', '36', 'D2', '50', '68', '9E', '62', '71', '15', '3D', 'D6', '40', 'C4', 'E2', '0F'],
        ['8E', '83', '77', '6B', '25', '05', '3F', '0C', '30', 'EA', '70', 'B7', 'A1', 'E8', 'A9', '65'],
        ['8D', '27', '1A', 'DB', '81', 'B3', 'A0', 'F4', '45', '7A', '19', 'DF', 'EE', '78', '34', '60']];
    sbox[1] = [
        ['55', 'C2', '63', '71', '3B', 'C8', '47', '86', '9F', '3C', 'DA', '5B', '29', 'AA', 'FD', '77'], 
        ['8C', 'C5', '94', '0C', 'A6', '1A', '13', '00', 'E3', 'A8', '16', '72', '40', 'F9', 'F8', '42'], 
        ['44', '26', '68', '96', '81', 'D9', '45', '3E', '10', '76', 'C6', 'A7', '8B', '39', '43', 'E1'], 
        ['3A', 'B5', '56', '2A', 'C0', '6D', 'B3', '05', '22', '66', 'BF', 'DC', '0B', 'FA', '62', '48'], 
        ['DD', '20', '11', '06', '36', 'C9', 'C1', 'CF', 'F6', '27', '52', 'BB', '69', 'F5', 'D4', '87'], 
        ['7F', '84', '4C', 'D2', '9C', '57', 'A4', 'BC', '4F', '9A', 'DF', 'FE', 'D6', '8D', '7A', 'EB'], 
        ['2B', '53', 'D8', '5C', 'A1', '14', '17', 'FB', '23', 'D5', '7D', '30', '67', '73', '08', '09'], 
        ['EE', 'B7', '70', '3F', '61', 'B2', '19', '8E', '4E', 'E5', '4B', '93', '8F', '5D', 'DB', 'A9'], 
        ['AD', 'F1', 'AE', '2E', 'CB', '0D', 'FC', 'F4', '2D', '46', '6E', '1D', '97', 'E8', 'D1', 'E9'], 
        ['4D', '37', 'A5', '75', '5E', '83', '9E', 'AB', '82', '9D', 'B9', '1C', 'E0', 'CD', '49', '89'], 
        ['01', 'B6', 'BD', '58', '24', 'A2', '5F', '38', '78', '99', '15', '90', '50', 'B8', '95', 'E4'], 
        ['D0', '91', 'C7', 'CE', 'ED', '0F', 'B4', '6F', 'A0', 'CC', 'F0', '02', '4A', '79', 'C3', 'DE'], 
        ['A3', 'EF', 'EA', '51', 'E6', '6B', '18', 'EC', '1B', '2C', '80', 'F7', '74', 'E7', 'FF', '21'], 
        ['5A', '6A', '54', '1E', '41', '31', '92', '35', 'C4', '33', '07', '0A', 'BA', '7E', '0E', '34'], 
        ['88', 'B1', '98', '7C', 'F3', '3D', '60', '6C', '7B', 'CA', 'D3', '1F', '32', '65', '04', '28'], 
        ['64', 'BE', '85', '9B', '2F', '59', '8A', 'D7', 'B0', '25', 'AC', 'AF', '12', '03', 'E2', 'F2']];
    sbox[2] = sbox[0]
    sbox[3] = sbox[1]
    list_out = [0] * 32

    for i in range(0, 4):
        list_tmp = list_in[8*i:8*(i+1)]
        hex_tmp = binvec2hex(list_tmp)
        row_tmp, col_tmp = hex2dec(hex_tmp[0]), hex2dec(hex_tmp[1])
        hex_tmp_s = sbox[i][row_tmp][col_tmp]
        list_out[8*i:8*(i+1)] = hex2binvec(hex_tmp_s)
    return list_out


def linearTransform(list_in, typex):
    # list_in = list(map(int, list_in))
    if typex == 1:
        shift_bits_list = [0, 2, 10, 18, 24]
    else:
        shift_bits_list = [0, 8, 14, 22, 30]

    list_out = [0] * len(list_in)
    for i in range(0,len(shift_bits_list)):
        list_out = binaryXor(list_out, circShiftLeft(list_in, shift_bits_list[i]))

    return list_out


def varsInit():
    global k_hex, k, v_hex, v, d, s, r1, r2
    # k_hex = ['01','23','45','67','89','AB','CD','EF','01','23','45','67','89','AB','CD','EF']
    k_hex = ['00','00','00','00','00','00','00','00','00','00','00','00','00','00','00','00']
    for i in range(0, 16):
        k[i] = hex2binstr(k_hex[i])

    v_hex = ['00','00','00','00','00','00','00','00','00','00','00','00','00','00','00','00']
    for i in range(0, 16):
        v[i] = hex2binstr(v_hex[i])

    for i in range(0, 16):
        s[i] = k[i] + d[i] + v[i]
        s[i] = list(map(int,s[i]))
    r1 = [0] * 32
    r2 = [0] * 32

def lfsrInit():
    global k_hex, k, v_hex, v, d, s, w
    shift_bits_list = [15, 17, 21, 20, 8, 0]
    shift_index_list = [15, 13, 10, 4, 0, 0]
    xv = [0] * 31
    for i in range(0, len(shift_bits_list)):
        s_i_shifted = circShiftLeft(s[shift_index_list[i]], shift_bits_list[i])
        xv = modAdd_2e31m1(xv, s_i_shifted)
    s[16] = modAdd_2e31m1(shiftLeft(w, -1), xv) # The only diffrence of lfsrWork() and lfsrInit()
    if s[16] == [0]*31:
        s[16] = [1]*31
    for i in range(0,16):
        s[i] = s[i+1]

def lfsrWork():
    global k_hex, k, v_hex, v, d, s
    shift_bits_list = [15, 17, 21, 20, 8, 0]
    shift_index_list = [15, 13, 10, 4, 0, 0]
    xv = [0] * 31
    for i in range(0, len(shift_bits_list)):
        s_i_shifted = circShiftLeft(s[shift_index_list[i]], shift_bits_list[i])
        xv = modAdd_2e31m1(xv, s_i_shifted)
    s[16] = xv # The only diffrence of lfsrWork() and lfsrInit()
    if s[16] == [0]*31:
        s[16] = [1]*31
    for i in range(0,16):
        s[i] = s[i+1]

def nonLinearFunction():
    global w, x, r1, r2
    w = binaryAdd(binaryXor(x[0], r1), r2)
    w1 = binaryAdd(r1, x[1])
    w2 = binaryXor(r2, x[2])
    r1 = sboxOfZuc(linearTransform(w1[-16:]+w2[0:16], 1))
    r2 = sboxOfZuc(linearTransform(w2[-16:]+w1[0:16], 2))

def bitReorganization():
    global x, s
    x[0] = s[15][0:16] + s[14][-16:]
    x[1] = s[11][-16:] + s[9][0:16]
    x[2] = s[7][-16:] + s[5][0:16]
    x[3] = s[2][-16:] + s[0][0:16]

def zucInit():
    global k_hex, k, v_hex, v, d, s, r1, r2, x, w
    for i in range(0, 32):
        print('zucInit(): {}'.format(i))
        # print(list(map(binvec2hex, [x[0], x[1], x[2],x[3], r1, r2, binaryXor(x[3],w), s[15]])))
        bitReorganization()
        nonLinearFunction()
        lfsrInit()

def zucWork(i=0):
    global k_hex, k, v_hex, v, d, s, r1, r2, x, w
    bitReorganization()
    nonLinearFunction()
    key_bin = binaryXor(w, x[3])
    key_hex = binvec2hex(key_bin)
    if i != 0:
        print('Key {:>02} {}'.format(i, key_hex.lower()))
    lfsrWork()

def outputKey(num=1):
    global k_hex, k, v_hex, v, d, s, r1, r2, x, w
    for i in range(0, num+1):
        zucWork(i)

if __name__ == '__main__':
    varsInit()
    zucInit()
    outputKey(4)