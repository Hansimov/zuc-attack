# A typical format of *.trs is TLV: Tag + Length + Value
# 
# --------------------------------------------------------------------------------------------- %
# Tag   Name  M/O   Type    Length   Default     Meaning
# ---------------------------------------------------------------------------------------------
# 0x41   NT    M    int       4                  Number of traces
# 0x42   NS    M    int       4                  Number of samples per trace
# 0x43   SC    M    byte      1                  Sample coding (see table below)
# 0x44   DS    O    short     2       0          Length of cryptographic data included in trace
# 0x45   TS    O    byte      1       0          Title space reserved per trace
# 0x46   GT    O    byte[]    var     "trace"    Global trace title
# 0x47   DC    O    byte[]    var     None       Description
# 0x48   XO    O    int       4       0          Offset in X-axis for trace representation
# 0x49   XL    O    byte[]    var     None       Label of X-axis (ASCII)
# 0x4A   YL    O    byte[]    var     None       Label of Y-axis (ASCII)
# 0x4B   XS    O    float     4       1          Scale value for X-axis
# 0x4C   YS    O    float     4       1          Scale value for Y-axis
# 0x4D   TO    O    int       4       0          Trace offset for displaying trace numbers
# 0x4E   LS    O    byte      1       0          Logarithmic scale
# 0x4F-  -     -    -         -       -          -
# -0x5E  -     -    -         -       -          Reserved for future use
# 0x5F   TB    M    none      0                  Trace block marker: an empty TLV that marks
#                                                the end of the header
# ----------------------------------------------------------------------------------------------
# * 'var' in Length means 'variable'.
# 
# * SC defines the sample coding:
# 
#   bit 8-6   reserved, set to '000'
#   bit 5     integer (0) or floating point (1)
#   bit 4-1   Sample length in bytes (valid values are 1, 2, 4)
# 
# ---------------------------------------------------------------------------------------------- %
# The object coding always starts with the tag byte.
# The object length is coded in one or more bytes.
# If bit 8 (MSB) is set to '1', the remaining 7 bits indicate the length of the object.
# If bit 8 (MSB) is set to '0', the remaining 7 bits indicate the number of additional bytes
  # in the length field.
# These additional bytes define the length in little endian coding (LSB first).
# The content of the object is stored in the subsequent number of bytes,
#   indicated by length.
# A trace set file contains at least the mandatory objects
#   and may contain any of the optional fields.
# The TB object is always the last object and marks the end of the header.
# The value of the numeric objects is coded little endian (LSB first).
# The float values use the IEEE 754 coding which is commonly supported by
#   modern programming languages.
# 
# ---------------------------------------------------------------------------------------------- %
# 
# ---------------------------------------------------------------------------------------------- %
# Assume there is a trace set like this:
# 
# 41 [04] (DB 03 00 00) 42 [04] (E8 03 00 00) 43 [01] (14) 44
# [02] (10 00) 45 [01] (0A) 49 [03] (73 65 63) 4B [04] (E8 52 96
# 34) 5F [00] 20 20 20 20 20 ...
# 
# 0x41 (NT), length: 4, value: 0x03DB     (987)     number of traces
# 0x42 (NS), length: 4, value: 0x03E8     (1000)    number of samples
# 0x43 (SC), length: 1, value: 0x14       (20)      float,  4 bytes per sample
# 0x44 (DS), length: 2, value: 0x10       (16)      Data Size: 16 bytes
# 0x45 (TS), length: 1, value: 0x0A       (10)      10 bytes title space per trace
# 0x49 (XL), length: 3, value: 0x736563   (sec)     X-axis Label
# 0x4B (XS), length: 4, value: 0x349652E8 (280E-9)  time base of 280ns per sample
# 0x5F (TB), length: 0,                             beginning of trace block
# 
# 987 traces: 10 bytes space (title not present)
#             16 bytes data (e.g. 0x69 0x6A .. 0x56 0x00)
# 4000 bytes: 1000 float samples of 4 bytes (e.g. 0x43970000 = 302)
# Note: The header length is flexible, but always ends with the Trace Block Marker: 0x5F00.

# ---------------------------------------------------------------------------------------------- %

import numpy as np
import struct
import time
import sys
import pickle
from convertType import *

# trsfilename = 'celcom.trs'
trsfilename = 'zuc_traces.trs'

class TrsTag:
    def __init__(self, hexstr, val, desc):
        self.hexstr = hexstr
        self.val    = val
        self.desc   = desc

def readValueOfTag(fid):
    lem = hex2dec(fid.read(1).hex())
    hex_str = fid.read(lem).hex()
    return hex_str

def parseSampleCoding(sc_hex):
    # Sample Coding: (trs_info['sc'] e.g.: '01')
    #    0000 0001
    #   <0123 4567>
    #
    #   bit 0-2   reserved, set to '000'
    #   bit 3     integer (0) or floating point (1)
    #   bit 4-7   Sample length in bytes (valid values are 1, 2, 4)

    sc_type_num = sc_hex[0]
    sc_size = int(sc_hex[1])

    if   sc_type_num == '0':
        if   sc_size == 1: # Integer
            sc_type = 'b' # signed char(int) - 1 byte
        elif sc_size == 2:
            sc_type = 'h' # signed short - 2 bytes
        elif sc_size == 4:
            sc_type = 'l' # signed long - 4 bytes
        else:
            print('Invalid Sample Size!')
            return
    elif sc_type_num == '1': # Floating
        if   sc_size == 4:
            sc_type = 'f' # float - 4 bytes
        else:
            print('Invalid Sample Size!')
            return
    else:
        print('Invalid Sample Type')
        return

    return sc_type, sc_size

def readHeader(fid):
    trs_info = {}
    trs_info['nt'] = TrsTag('', 0, 'Number of Traces')
    trs_info['ns'] = TrsTag('', 0, 'Number of Samples')
    trs_info['sc'] = TrsTag('', 0, 'Sample Coding')
    trs_info['st'] = TrsTag('', 'b', 'Sample Type')
    trs_info['ss'] = TrsTag('', 1, 'Sample Size (Bytes)')
    trs_info['ds'] = TrsTag('', 0, 'Data Size')
    trs_info['ts'] = TrsTag('', 0, 'Title Space')
    trs_info['gt'] = TrsTag('', 'trace','Global Title')
    trs_info['dc'] = TrsTag('', '', 'Description')
    trs_info['xo'] = TrsTag('', 0, 'X-axis Offset')
    trs_info['xl'] = TrsTag('', '', 'X-axis Label')
    trs_info['yl'] = TrsTag('', '', 'Y-axis Label')
    trs_info['xs'] = TrsTag('', 1, 'X-axis Scale')
    trs_info['ys'] = TrsTag('', 1, 'Y-axis Scale')
    trs_info['to'] = TrsTag('', 0, 'Trace Offset')
    trs_info['ls'] = TrsTag('', 0, 'Log Scale')
    tag = fid.read(1).hex().upper()

    readmode = 1
    while readmode == 1:
        hex_str = readValueOfTag(fid)

        if tag == '41':
            val = hex2int32(hex_str)
            trs_info['nt'] = TrsTag(hex_str, val, 'Number of Traces')
        elif tag == '42':
            val = hex2int32(hex_str)
            trs_info['ns'] = TrsTag(hex_str, val, 'Number of Samples')
        elif tag == '43':
            val = hex_str
            trs_info['sc'] = TrsTag(hex_str, val, 'Sample Coding')
            sc_type, sc_size = parseSampleCoding(val)
            trs_info['st'] = TrsTag(hex_str[0], sc_type, 'Sample Type')
            trs_info['ss'] = TrsTag(hex_str[1], sc_size, 'Sample Size (bytes)')
        elif tag == '44':
            val = hex2dec(hex_str[0:2])
            trs_info['ds'] = TrsTag(hex_str, val, 'Data Size (bytes)')
        elif tag == '45':
            val = hex_str
            trs_info['ts'] = TrsTag(hex_str, val, 'Title Space')
        elif tag == '46':
            val = hex2ascii(hex_str)
            trs_info['gt'] = TrsTag(hex_str, val, 'Global Title')
        elif tag == '47':
            val = hex2ascii(hex_str)
            trs_info['dc'] = TrsTag(hex_str, val, 'Description')
        elif tag == '48':
            val = hex2int32(hex_str)
            trs_info['xo'] = TrsTag(hex_str, val, 'X-axis Offset')
        elif tag == '49':
            val = hex2ascii(hex_str)
            trs_info['xl'] = TrsTag(hex_str, val, 'X-axis Label')
        elif tag == '4A':
            val = hex2ascii(hex_str)
            trs_info['yl'] = TrsTag(hex_str, val, 'Y-axis Label')
        elif tag == '4B':
            val = hex2float(hex_str)
            val = (floatSciNote(val,4))
            trs_info['xs'] = TrsTag(hex_str, val, 'X-axis Scale')
        elif tag == '4C':
            val = hex2float(hex_str)
            val = (floatSciNote(val,4))
            trs_info['ys'] = TrsTag(hex_str, val, 'Y-axis Scale')
        elif tag == '4D':
            val = hex2int(hex_str)
            trs_info['to'] = TrsTag(hex_str, val, 'Trace Offset')
        elif tag == '4E':
            val = hex_str
            trs_info['ls'] = TrsTag(hex_str, val, 'Log Scale')
        elif tag == '5F':
            readmode = 2; # Jump out of while loop: avoid executing tag reading below
            break;
        else:
            print('Invalid tag: {}'.format(tag))
            break

        tag = fid.read(1).hex().upper()

    return trs_info

# Use OOP is too slow
# class Trace(object):
#     def __init__(self, data, sample):
#         self.data   = data
#         self.sample = sample

def readData(fid, data_size):
    data = fid.read(data_size).hex()
    return data

def readSample(fid, sample_num, sample_type):
    sample_row = [0] * sample_num
    for i in range(0, sample_num):
        sample_hex = fid.read(1).hex()
        sample_row[i] = struct.unpack(sample_type, bytearray.fromhex(sample_hex))[0]
    return sample_row

def parseData(data):
    init_vec = data[0:16]
    first_cipher_text = data[16:24]
    return init_vec, first_cipher_text

def plotSample(data):
    pass

t1 = time.time()

with open(trsfilename,'rb') as trsfile:
    trs_info = readHeader(trsfile)

    print('\n')
    print('| {:-<3} | {:-<20} | {:-<10} | {:->10} |'.format('', '', '', ''))
    print('| {:<3} | {:<20} | {:<10} | {:>10} |'.format('Key', 'Description', 'Hex', 'Value'))
    print('| {:-<3} | {:-<20} | {:-<10} | {:->10} |'.format('', '', '', ''))
    for key, item in trs_info.items():
        print('| {:<3} | {:<20} | {:<10} | {:>10} |'.format(key, item.desc, item.hexstr, item.val))
    print('| {:-<3} | {:-<20} | {:-<10} | {:->10} |'.format('', '', '', ''))

    print('\n')


    trace_bgn, trace_end = 0, 0
    data_mat = [''] * num
    # data_mat = []
    # sample_mat = np.zeros((1,trs_info['ns'].val), dtype='int8')
    sample_mat = [0] * num
    # sample_mat = []

    for i in range(trace_bgn, trace_end+1):
        sys.stdout.write('\r>>> Reading trace: {:0>7}'.format(i))
        # sys.stdout.flush()
        data_row = readData(trsfile, trs_info['ds'].val)
        # sample_row = [i] * 10
        sample_row = readSample(trsfile, trs_info['ns'].val, trs_info['st'].val)

        data_mat[i] = data_row
        # data_mat.append(data_row)

        # sample_mat = np.vstack([sample_mat, sample_row])
        sample_mat[i] = sample_row
        # sample_mat.append(sample_row)

    # with open('zuc_sample.txt','a') as zuc_sample_file:
    #     np.savetxt(zuc_sample_file, sample_mat)

    # print(data_mat)
    # print(sample_mat)

    t2 = time.time()
    print('\n')
    print('Time of reading: ',t2-t1)

    print('\n')
    with open('zuc_sample.txt','w') as zuc_sample_file:
        # pickle.dump(sample_mat, zuc_sample_file)
        for i in range(0, num):
            sys.stdout.write('\r<<< Dumping trace: {:0>7}'.format(i))
            for col in sample_mat[i]:
                print(col, end = ' ', file=zuc_sample_file)
            print('', file=zuc_sample_file)
    # with open('zuc_sample.txt','r') as zuc_sample_file:
    #     xx = pickle.load(zuc_sample_file)
    # print(type(xx[0][0]))

    t3 = time.time()
    print('\n')
    print('Time of writing: ',t3-t2)
    print('\n')
