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


trsfilename = 'celcom.trs'

class TrsTag:
    def __init__(self,val,str):
        self.val = val
        self.str = str


# What's the correct way to convert bytes to a hex string in Python 3?
#   https://stackoverflow.com/a/36149089/8328786
# https://docs.python.org/3/library/stdtypes.html#bytes.hex
trs_tag_dict = {}
with open(trsfilename,'rb') as trsfile:
    for i in range(1,10):
        a = trsfile.read(1)
        # print(a.hex())
        tmp = TrsTag(a.hex(),i**2)
        dd[i] = tmp
        print(dd[i].val)


for key,val in dd.items():
    print(key,val.str)

