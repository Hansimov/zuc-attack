import struct
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import heapq

from convertType import *
from binaryOperation import *
from zucAlgo import linearTransform, sboxOfZuc, d
from parseTrace import *

trs_file_name = 'zuc_traces.trs'
with open(trs_file_name, 'rb') as trs_file:
    trs_info = readHeader(trs_file)
    header_end = trs_file.tell()

def getTraceInitVector(fid, header_end, trace_index):
    # 32 bytes == 64 hex chars
    # e235a8fc2c876201c40a3c853cd389e4 71375fe8 000000000000000000000000
    # 91bf437bbbb5450c832bba6395ecd63a 9894454c 000000000000000000000000
    # d618c45bf76cdf044bc3248fd5dde752 27dd16c1 000000000000000000000000
    # a660c6c5661cdce2309337d2a3b98bc5 65acde9a 000000000000000000000000
    # 35f82722cb7729e0879cee33e1d0cd6c fb78e227 000000000000000000000000
    # fa82051a2c6ef376e61f89feb7b2fb5f 7b179ddf 000000000000000000000000
    # a8debb98cf31a85d219c83b98832a2f8 5b4bfcd2 000000000000000000000000
    # 362de8c43832f48e4ed69930fa608ed0 916f6ba6 000000000000000000000000
    # d7d067072c21c442c1ccc969f18dcebf cbc0917f 000000000000000000000000
    # 0169570ab0f046f30fc04faf934aaddf df18c765 000000000000000000000000
    pointer_pos = header_end + trace_index * (trs_info['ds'].val + trs_info['ns'].val)
    fid.seek(pointer_pos, 0)

    init_vec_hex = fid.read(trs_info['ds'].val).hex()
    return init_vec_hex[0:32]

def getTraceSample(fid, header_end, trace_index, sample_num=1, offset=1300):
    pointer_pos = header_end + trace_index * (trs_info['ds'].val + trs_info['ns'].val) \
                 + trs_info['ds'].val + offset
    fid.seek(pointer_pos, 0)
    # sample_num = trs_info['ns'].val
    # sample_num = 1
    sample_row = readSample(fid, sample_num, trs_info['st'].val)
    return sample_row

# def guessKey():
#     k9_guess = [[0]*8]*256
#     k5_guess = [[0]*8]*256
#     for i in range(0, 256):
#         k9_guess[i] = dec2binvec(i,8)
#         k5_guess[i] = dec2binvec(i,8)
#     pass

# k_correct = '01 23 45 67 89 AB CD EF 01 23 45 67 89 AB CD EF'
#               0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
# k[9]: 23 => 0010 0011
# k[5]: AB => 1010 1011


### Round 1 ###
# 
# ↓  ↓  ↓  ↓  ↓
# x1 = s[11][-16:]+s[9][0:16]
# x2 = s[7][-16:]+s[5][0:16]
# ↓  ↓  ↓  ↓  ↓
# x1 = d[11][-8:] + v[11][:]  +  k[9][:] + d[9][0:8]
# x2 = d[7][-8:] + v[7][:]  +  k[5][:] + d[5][0:8]
# ↓  ↓  ↓  ↓  ↓
# r1 = S(L1(w1L+w2H))
# r2 = S(L2(w2L+w1H))
# ↓  ↓  ↓  ↓  ↓
# w1 = x1
# w2 = x2
# ↓  ↓  ↓  ↓  ↓
# w1L = x1[-16:] = k[9][:] + d[9][0:8]
# w2H = x2[0:16] = d[7][-8:] + v[7][:]
# w2L = x2[-16:] = k[5][:] + d[5][0:8]
# w1H = x1[0:16] = d[11][-8:] + v[11][:]
# ↓  ↓  ↓  ↓  ↓
# r1 = sboxOfZuc(linearTransform(w1L+w2H, 1))
# r2 = sboxOfZuc(linearTransform(w2L+w1H, 2))
# ↓  ↓  ↓  ↓  ↓
# r1 = sboxOfZuc(linearTransform(x1[-16:] + x2[0:16] , 1)) # Related to k9
# r2 = sboxOfZuc(linearTransform(x2[-16:] + x1[0:16] , 2)) # Related to k5

def calcInterValue(init_vec_hex, k9=[0]*8, k5=[0]*8, N=1):
    global d
    # v = ['01010101']*16
    # v = [list(map(int, v_item)) for v_item in v]
    v = [[0]*8 for _ in range(16)]
    for i in range(0,16):
        init_vec_byte = init_vec_hex[2*i:2*i+2]
        v[i] = hex2binvec(init_vec_byte)

    d = [list(map(int, d_item)) for d_item in d]

    x1 = (d[10+N][-8:] + v[10+N][:]) + (k9[:] + d[8+N][0:8])
    x2 = (d[ 6+N][-8:] + v[ 6+N][:]) + (k5[:] + d[4+N][0:8])

    r1 = sboxOfZuc(linearTransform(x1[-16:]+x2[0:16], 1)) # Related to k9
    r2 = sboxOfZuc(linearTransform(x2[-16:]+x1[0:16], 2)) # Related to k5
    # print(binvec2hex(r1))
    # print(binvec2hex(r2))
    return r1, r2

# calcInterValue('0'*32, k9=[0]*8)


def calcCorrelation(num_of_trace, sigma_xy, sigma_x2, sigma_y2, average_x, average_y):
    try:
        corr_val = (sigma_xy - num_of_trace * average_x * average_y) \
             / (math.sqrt(sigma_x2 - num_of_trace * average_x**2)) \
             / (math.sqrt(sigma_y2 - num_of_trace * average_y**2))
    except Exception as e:
        corr_val = 'nan'

    return corr_val #, sigma_xy, sigma_x2, sigma_y2, average_x, average_y

def calcHammingWeight(arr_in):
    if isinstance(arr_in, str):
        list_in = list(map(int, arr_in))
    else:
        list_in = arr_in

    hw = 0
    for bit in list_in:
        hw += bit

    return hw

if __name__ == '__main__':
    t1 = time.time()
    trs_file_name = 'zuc_traces.trs'

    with open(trs_file_name, 'rb') as trs_file:
        # trs_info = readHeader(trs_file)
        # header_end = trs_file.tell()

        trace_num = 10

        # sample_num = trs_info['ns'].val
        sample_num = 1

        initvec_mat = [[]]*trace_num
        sample_mat = [[]]*trace_num

        plt.figure(num=None, figsize=(20, 9), dpi=80, facecolor='w', edgecolor='k')

        for i in range(0, trace_num):
            sys.stdout.write('\r>>> Reading trace: {}'.format(i+1))
            initvec_mat[i] = getTraceInitVector(trs_file, header_end, i)
            sample_mat[i] = getTraceSample(trs_file, header_end, i, sample_num, 1300)
            # plt.cla()
            # plt.plot(sample_mat[i])
            # plt.pause(0.01)
        # plt.show()

        k_all = [[0]*8 for _ in range(256)]
        for k in range(0,256):
            k_all[k] = dec2binvec(k, 8)

        sample_mat = np.array(sample_mat)

        corr_mat     = [ [0]*sample_num for _ in range(256)]
        corr_avg     = [0]*256
        interval_mat = [ [0]*trace_num for _ in range(256)]

        hw_mat = [[0]*trace_num for _ in range(256)]

        print('')
        inter_val_1_file = open('inter_val_1.txt','r')
        aa = inter_val_1_file.readline()
        print(list(map(int, aa.strip())))

        # print('\n')
        # for k in range(0, 256):
        #     print('>>> Calulating inter values of guessing key: {}'.format(k))
        #     for i in range(0, trace_num):
        #         k_guess = k_all[k]
        #         # interval_mat[k][i], _ = calcInterValue(initvec_mat[i], k9=k_guess)
        #         # _, interval_mat[k][i] = calcInterValue(initvec_mat[i], k5=k_guess)
        #         hw_mat[k][i] = calcHammingWeight(interval_mat[k][i])
        #     print('')

        # corr_max = [[0]*1 for _ in range(256)]
        # for k in range(0,256):
        #     print('>>> Calulating correlation matrix of guessing key: {}'.format(k))
        #     for j in range(0, sample_num):
        #         corr_mat[k][j] = np.corrcoef(hw_mat[k], sample_mat[:,j])[0][1]
        #     # print(np.mean(corr_mat[k]))
        #     # plt.cla()
        #     # plt.plot(corr_mat[k])
        #     # plt.pause(0.01)

        #     corr_max[k] = heapq.nlargest(len(corr_max[0]), corr_mat[k])
        #     corr_avg[k] = np.mean(corr_max[k])
        #     print('--- {}: {}'.format(dec2hex(k), corr_avg[k]))

        t2 = time.time()
        print('Time of processing: {} s'.format(t2-t1))

        # plt.plot(corr_avg)
        # plt.show()





