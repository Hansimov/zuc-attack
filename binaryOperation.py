def circShiftLeftOfList(list_in, bits=1):
    list_out = [0] * len(list_in)
    if bits >= 0:
        bits = bits % len(list_in)
        list_out[-bits:] = list_in[0:bits]
        list_out[0:-bits] = list_in[bits:]
    else:
        bits = (-bits) % len(list_in)
        list_out[0:bits] = list_in[-bits:]
        list_out[bits:] = list_in[0:-bits]
    return list_out

def circShiftLeft(arr_in, bits=1):
    if   isinstance(arr_in,str):
        # In Python, string is immutable, so I convert string to list first
        list_in = list(arr_in)
        list_out = circShiftLeftOfList(list_in, bits)
        arr_out = ''.join(list_out)
    elif isinstance(arr_in, list):
        list_in = arr_in
        list_out = circShiftLeftOfList(list_in, bits)
        arr_out = list_out
    return arr_out

def shiftLeftOfList(list_in, bits=1):
    if abs(bits) >= len(list_in):
        list_out = []
        return list_out

    list_out = [0] * (len(list_in)-abs(bits))
    if bits >= 0:
        bits = abs(bits) % len(list_in)
        list_out[0:] = list_in[bits:]
    else:
        bits = abs(bits) % len(list_in)
        list_out[0:] = list_in[0:-bits]
    return list_out

def shiftLeft(arr_in, bits=1):
    if   isinstance(arr_in, str):
        list_in = list(arr_in)
        list_out = shiftLeftOfList(list_in, bits)
        arr_out = ''.join(list_out)
    elif isinstance(arr_in, list):
        list_in = arr_in
        list_out = shiftLeftOfList(list_in, bits)
        arr_out = list_out
    return arr_out


def bitAdd(a,b,c):
    if   a + b + c == 0:
        sum_bit = 0
        carry_bit = 0
    elif a + b + c == 1:
        sum_bit = 1
        carry_bit = 0
    elif a + b + c == 2:
        sum_bit = 0
        carry_bit = 1
    elif a + b + c == 3:
        sum_bit = 1
        carry_bit = 1
    else:
        pass
    return sum_bit, carry_bit

def binaryAdd(bits, bit_list1, bit_list2):
    bit_list1 = list(map(int, bit_list1))
    bit_list2 = list(map(int, bit_list2))
    # print(bit_list2)
    bit_list1.reverse()
    bit_list2.reverse()
    sum_list   = [0] * bits
    carry_list = [0] * (bits+1)
    for i in range(0, bits):
        sum_list[i], carry_list[i+1] = bitAdd(bit_list1[i], bit_list2[i], carry_list[i])
    sum_list.reverse()
    carry_list.reverse()
    return sum_list, carry_list

def mod_2e31m1(bit_list1, bit_list2):
    sum_list, carry_list = binaryAdd(31, bit_list1, bit_list2)
    # print(sum_list)
    carry_list_x = [0]*31
    carry_list_x.append(carry_list[31])
    sum_list, _ = binaryAdd(31, sum_list, carry_list_x)
    return sum_list


def bitXor(*args):
    xor_result = [0] * len(args[0])
    for i in range(0, len(args)):
        bit_list_tmp = list(map(int, args[i]))
        for i in range(0, len(bit_list_tmp)):
            if bit_list_tmp[i] == xor_result[i]:
                xor_result[i] = 0
            else:
                xor_result[i] = 1
    return(xor_result)
