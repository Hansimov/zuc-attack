# from array import array
# with open('inter_val.bin','wb') as outfile:
#     arr = array('d',[1,2,3])
#     arr.tofile(outfile)

# with open('inter_val.bin', 'rb') as infile:
#     brr = array('d')
#     brr.fromstring(infile.read())
#     print(brr)

from zucAttack import *

# with open('inter_val_1.txt','w') as outfile:
#     for i in range(0, 1000000):
#         sys.stdout.write('\rProcessing {}'.format(i))
#         # print(str(1)*32,file=outfile)

# trs_file_name = 'zuc_traces.trs'
# with open(trs_file_name, 'rb') as trs_file:
    # trs_info = readHeader(trs_file)
    # header_end = trs_file.tell()

if __name__ == '__main__':

    t1 = time.time()

    with open(trs_file_name, 'rb') as trs_file:
        trace_num = 10000

        k_all = [[0]*8 for _ in range(256)]
        for k in range(0,256):
            k_all[k] = dec2binvec(k, 8)

        inter_val_1_file = open('inter_val_1.txt','w')
        inter_val_2_file = open('inter_val_2.txt','w')

        for i in range(0, trace_num):
            sys.stdout.write('\r>>> Calculating inter value: {}'.format(i))
            init_vec_hex = getTraceInitVector(trs_file, header_end, i)

            for k in range(0, 256):
                r1, r2 = calcInterValue(init_vec_hex, k9=k_all[k], k5=k_all[k])
                r1_str = ''.join(str(item) for item in r1)
                r2_str = ''.join(str(item) for item in r2)

                print(r1_str, file=inter_val_1_file)
                print(r2_str, file=inter_val_2_file)

    t2 = time.time()
    print('')
    print('Time of writing invter value 1: {:.6} s'.format(t2-t1))