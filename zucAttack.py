import struct
import time

from convertType import *
from binaryOperation import *
from zucAlgo import linearTransform, sboxOfZuc, d
from parseTrace import *

def getInitVector(trace_num=1):
    pass
    return []

def guessKey():
    k9_guess = [[0]*8]*256
    k5_guess = [[0]*8]*256
    for i in range(0, 256):
        k9_guess[i] = dec2binvec(i,8)
        k5_guess[i] = dec2binvec(i,8)
    pass


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



def calcInterValue(k5=[0]*8, k9=[0]*8, N=1):
    global d, v
    # v = getInitVector()
    v = ['01010101']*16
    v = [list(map(int, v_item)) for v_item in v]

    d = [list(map(int, d_item)) for d_item in d]

    x1 = (d[10+N][-8:] + v[10+N][:]) + (k9[:] + d[8+N][0:8])
    x2 = (d[ 6+N][-8:] + v[ 6+N][:]) + (k5[:] + d[4+N][0:8])

    r1 = sboxOfZuc(linearTransform(x1[-16:]+x2[0:16], 1)) # Related to k9
    r2 = sboxOfZuc(linearTransform(x2[-16:]+x1[0:16], 2)) # Related to k5
    print(r1)
    print(r2)
    return r1, r2


# calcInterValue()

def calcCorrMatrix():
    pass

def calcHammingWeight(arr_in):
    if isinstance(arr_in, str):
        list_in = list(map(int, arr_in))
    else:
        list_in = arr_in

    hw = 0
    for bit in list_in:
        hw += bit

    return hw


