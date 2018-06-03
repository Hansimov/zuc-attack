import struct
import time
import math
import numpy as np
import heapq
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei'] # 正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False   # 正常显示负号
plt.rc('font', size=12)

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

def getTraceSample(fid, header_end, trace_index, sample_num=1, offset=0):
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

# ------------------- Find positions of leakage ------------------- #
    def findLeakage():
    # Reading traces
        trace_num = 20000
        sample_num = trs_info['ns'].val
        offset = 0

        sample_mat = [[]]*trace_num

        for i in range(0, trace_num):
            sys.stdout.write('\r>>> Reading trace: {}'.format(i+1))
            # initvec_mat[i] = getTraceInitVector(trs_file, header_end, i)
            sample_mat[i] = getTraceSample(trs_file, header_end, i, sample_num, offset)

    # Loading inter values and calculating hamming weights
        hw_mat_correct = [0] * trace_num

        key_2_index = hex2dec('AB') # correct k5 of inter_val_2
        inter_val_2_file = open('inter_val_2.txt','r')

        print('')
        for i in range(0, trace_num):
            inter_val_2_file.seek((i*256 + key_2_index)*34)
            inter_val_2_correct = inter_val_2_file.readline().strip()
            hw_mat_correct[i] = calcHammingWeight(inter_val_2_correct)

        # key_1_index = hex2dec('23') # correct k9 of inter_val_1
        # inter_val_1_file = open('inter_val_1.txt','r')

        # print('')
        # for i in range(0, trace_num):
        #     inter_val_1_file.seek((i*256 + key_1_index)*34)
        #     inter_val_1_correct = inter_val_1_file.readline().strip()
        #     hw_mat_correct[i] = calcHammingWeight(inter_val_1_correct)

        sample_mat = np.array(sample_mat)
        hw_mat_correct = np.array(hw_mat_correct)

    # Calculating correlations of each point in samples and plot them

        # plt.figure(figsize=(18,6), dpi=80)
        fig, ax1 = plt.subplots(figsize=(14,5), dpi=100)
        plt.xlabel('时间')
        # curve1 = ax1.plot(sample_mat[0], label='Power of trace', color='b')
        curve1 = ax1.plot(sample_mat[0], label='功耗曲线', color='b')
        ax1.set_ylabel('功耗')
        # ax1.yaxis.labelpad = 10

        ax2 = ax1.twinx()
        for n in [100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
        # for n in [100, 200, 500]:
        # for n in [trace_num]:
            corr_mat = [0] * sample_num
            for j in range(0, sample_num):
                corr_mat[j] = abs(np.corrcoef(hw_mat_correct[0:n], sample_mat[0:n,j])[0][1])
            ax2.cla()
            ax2.set_ylabel('相关系数（绝对值）')
            ax2.yaxis.labelpad = 10
            # curve2 = ax2.plot(corr_mat, label='Correlation coefficients', color='r')
            curve2 = ax2.plot(corr_mat, label='相关系数（绝对值）', color='r')
            
            curves = curve1 + curve2
            labels = [curve.get_label() for curve in curves]
            
            ax2.legend(curves, labels, loc=1)

            # image_name = './report/images/leakage_{}.png'.format(n)
            # print('Outputing {}'.format(image_name))
            # plt.savefig(image_name)

        t2 = time.time()
        print('Time of processing: {} s'.format(t2-t1))

        plt.show()

# ------------------- Attack traces by guessing didffent keys ------------------- #

    def attackTraces():
    # Reading traces
        trace_num = 100

        # sample_num = trs_info['ns'].val
        # sample_num = 600
        # sample_num = 1
        sample_num = 10

        # offset = 1640
        # offset = 1200
        offset = 1315

        # initvec_mat = [[]]*trace_num
        sample_mat = [[]]*trace_num

        # plt.figure(num=None, figsize=(20, 9), dpi=80, facecolor='w', edgecolor='k')

        for i in range(0, trace_num):
            sys.stdout.write('\r>>> Reading trace: {}'.format(i+1))
            # initvec_mat[i] = getTraceInitVector(trs_file, header_end, i)
            sample_mat[i] = getTraceSample(trs_file, header_end, i, sample_num, offset)
            # plt.cla()
            # plt.plot(sample_mat[i])
            # plt.pause(0.01)
        # plt.plot(sample_mat[i])
        # plt.show()


        # inter_val_mat = [ [0]*trace_num for _ in range(256)]

        hw_mat = [[0]*trace_num for _ in range(256)]


    # Loading inter values

        print('')
        inter_val_2_file = open('inter_val_2.txt','r')

        for i in range(0, trace_num):
            sys.stdout.write('\r>>> Loading inter values of trace: {}'.format(i))
            for k in range(0, 256):
                inter_val_2_str = inter_val_2_file.readline().strip()
                inter_val_2 = list(map(int, inter_val_2_str))
                hw_mat[k][i] = calcHammingWeight(inter_val_2)

        inter_val_2_file.close()

        # inter_val_1_file = open('inter_val_1.txt','r')

        # for i in range(0, trace_num):
        #     sys.stdout.write('\r>>> Loading inter values of trace: {}'.format(i))
        #     for k in range(0, 256):
        #         inter_val_1_str = inter_val_1_file.readline().strip()
        #         inter_val_1 = list(map(int, inter_val_1_str))
        #         hw_mat[k][i] = calcHammingWeight(inter_val_1)

        # inter_val_1_file.close()

    # Calculating correlation matrix of guessing key
        print('')

        sample_mat = np.array(sample_mat)
        hw_mat = np.array(hw_mat)


    # # 1.1 Plot changes of correlations of different keys with increasing number of traces

    #     trace_num_step = 100
    #     # trace_num_list = np.arange(99, 20000, 100)
    #     trace_num_list = np.arange(trace_num_step, trace_num+1, trace_num_step)

    #     corr_mat     = [ [0]*sample_num for _ in range(256)]
    #     corr_avg_mat = [[0]*len(trace_num_list) for _ in range(256)]

    #     nn = 0
    #     for n in trace_num_list:
    #         corr_maxn = [[0]*5 for _ in range(256)]
    #         sys.stdout.write('\rNumber of traces: {}'.format(n))
    #         for k in range(0,256):
    #             # print('>>> Calulating correlation matrix of guessing key: {}'.format(k))
    #             for j in range(0, sample_num):
    #                 corr_mat[k][j] = abs(np.corrcoef(hw_mat[k][0:n-1], sample_mat[0:n-1,j])[0][1])

    #             corr_maxn[k] = heapq.nlargest(len(corr_maxn[0]), corr_mat[k])
    #             corr_avg_mat[k][nn] = np.mean(corr_maxn[k])
    #         nn += 1

    #     fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

    #     for k in range(0, 256):
    #         ax.plot(trace_num_list, corr_avg_mat[k])

    #     ax.set_xlabel('使用的功耗曲线条数')
    #     ax.set_ylabel('相关系数（绝对值）')
    #     ax.xaxis.labelpad = 10
    #     ax.yaxis.labelpad = 10

    #     t2 = time.time()
    #     print('Time of processing: {} s'.format(t2-t1))
    #     image_name = './report/images/keyrank_{}_{}.png'.format(trace_num_list[-1], trace_num_step)
    #     print('Outputing {}'.format(image_name))
    #     plt.savefig(image_name)

    #     plt.show()

    # # 1.2 Plot mean correlations of different keys

    #     corr_mat     = [ [0]*sample_num for _ in range(256)]
    #     corr_avg     = [0]*256

    #     fig, ax = plt.subplots(figsize=(10, 5), dpi=100)

    #     for n in [100, 200, 500, 1000, 2000, 5000, 10000, 20000]:
    #     # for n in [100, 200]:
    #         corr_maxn = [[0]*5 for _ in range(256)]

    #         for k in range(0,256):
    #             # print('>>> Calulating correlation matrix of guessing key: {}'.format(k))
    #             for j in range(0, sample_num):
    #                 corr_mat[k][j] = abs(np.corrcoef(hw_mat[k][0:n], sample_mat[0:n,j])[0][1])

    #             corr_maxn[k] = heapq.nlargest(len(corr_maxn[0]), corr_mat[k])
    #             corr_avg[k] = np.mean(corr_maxn[k])
    #             print('--- Key {:03} {}: {:.6}'.format(k, dec2hex(k), corr_avg[k]))

    #         t2 = time.time()
    #         print('Time of processing: {} s'.format(t2-t1))

    #         ax.cla()
    #         ax.set_xlabel('猜测的密钥（十进制）')
    #         ax.set_ylabel('相关系数（绝对值）')
    #         ax.xaxis.labelpad = 10
    #         ax.yaxis.labelpad = 10
    #         ax.plot(range(0, 256), corr_avg, color='r')

    #         corr_max = max(corr_avg)
    #         key_max = corr_avg.index(corr_max)

    #         ax.vlines(x=key_max, ymin=0, ymax=corr_max, color='g', linestyle='--')
    #         x_ticks = np.append(ax.get_xticks(), key_max)
    #         ax.set_xticks(x_ticks)

    #         ax.get_xticklabels()[-1].set_color('g')

    #         ax.set_xlim([0, 255])
    #         ax.set_ylim([0, ax.get_ylim()[1]])

    #         # image_name = './report/images/keyguess_{}.png'.format(n)
    #         # print('Outputing {}'.format(image_name))
    #         # plt.savefig(image_name)

    #     plt.show()

# ------------------- Plot traces ------------------- #
    def plotTraces():

        sample_num = trs_info['ns'].val
        offset = 0

        sample_row = [0]*sample_num

        fig, ax = plt.subplots(figsize=(14, 5), dpi=100)

        trace_index_list = [1, 20, 200, 2000, 20000]
        # trace_index_list = [0]
        for i in trace_index_list:
            sys.stdout.write('\r>>> Reading trace: {}'.format(i))
            # initvec_mat[i] = getTraceInitVector(trs_file, header_end, i)
            sample_row = getTraceSample(trs_file, header_end, i-1, sample_num, offset)
            
            ax.cla()

            ax.set_xlabel('时间')
            ax.set_ylabel('功耗')

            ax.plot(sample_row, color='b')
            plt.title('曲线 - {:0>5}'.format(i), y=1.05)

            print('')
            image_name = './report/images/trace_{}.png'.format(i)
            print('Outputing {}'.format(image_name))
            plt.savefig(image_name)

        t2 = time.time()
        print('Time of processing: {} s'.format(t2-t1))

        plt.show()

# -------------------------------------------------------------------- #
    t1 = time.time()
    trs_file_name = 'zuc_traces.trs'

    with open(trs_file_name, 'rb') as trs_file:
        # findLeakage()
        # attackTraces()
        plotTraces()

