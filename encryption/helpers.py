import numpy as np
from sbox import sbox, sbox_inv
import coden


# ###################################
# HELPER FUNCTIONS
# #################################

# turn hexa chars to corresponding number, to use it in subBytes

def letter_to_number(letter):
    options = {
        'a': 10,
        'b': 11,
        'c': 12,
        'd': 13,
        'e': 14,
        'f': 15,
    }

    if letter.lower() in options.keys():
        return options[letter.lower()]


# if multiply by 2 we use this function

def multiply_by_2(v):
    m = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)
    if m[0] == '0':
        s = int(m, 2)
        s = s << 1
        s = bin(s)

        return s

    if m[0] == '1':
        s = int(m, 2)
        s = s << 1
        s = bin(s)

        _xor = int(s, 2) ^ int('00011011', 2)
        _xor = bin(_xor)

        return _xor


# if multiply by 3 we use this function

def multiply_by_3(v):
    m = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)

    m_2 = multiply_by_2(v)
    xor = int(m_2, 2) ^ int(m, 2)
    xor = bin(xor)

    return xor


def multiply_by_9(v, index=3):
    if index != 0:
        m = multiply_by_2(v)
        m = int(m, 2)
        m = format(m, '02x')[-2:]

        return multiply_by_9(m, index=index - 1)
    else:
        # hex to binary
        vb = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)
        return vb


def multiply_by_B(v):
    # hex to binary
    vb = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)

    # multiply by 9 with index = 2
    m_9 = multiply_by_9(v, index=2)

    # XOR
    _xor = int(vb, 2) ^ int(m_9, 2)

    # decimal to hexadecimal
    _xor = format(_xor, '02x')[-2:]

    # multiply bu 2
    m = multiply_by_2(_xor)

    # XOR
    _xor = int(vb, 2) ^ int(m, 2)
    return bin(_xor)


def multiply_by_D(v):
    # hex to binary
    vb = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)

    # multiply bu 2
    m = multiply_by_2(v)

    # XOR
    _xor = int(vb, 2) ^ int(m, 2)

    # decimal to hexadecimal
    _xor = format(_xor, '02x')[-2:]

    # multiply by 2
    m = multiply_by_9(_xor, index=2)

    _xor = int(vb, 2) ^ int(m, 2)

    return bin(_xor)


def multiply_by_E(v):
    vb = bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4)

    m = multiply_by_2(v)

    _xor = int(vb, 2) ^ int(m, 2)
    _xor = format(_xor, '02x')[-2:]

    m = multiply_by_2(_xor)

    _xor = int(vb, 2) ^ int(m, 2)
    _xor = format(_xor, '02x')[-2:]

    m = multiply_by_2(_xor)

    return m


# xor function to do XOR between hexa values in a input list
def xor(l):
    s = int('00000000', 2)
    for j, i in enumerate(l):
        s = s ^ int(i, 2)

    return format(s, '02x')[-2:]


# matrix_mul is a helper function of mix columns function, used to multiply shiftRows_mat by mix_column matrix

def matrix_mul(shiftrows_mat, mix_column):
    # list to store 2 values, to be used in the xor function
    xor_res = []

    # list to store xor results

    xor_mat = []

    # for each value in shiftRows matrix and mixColumns matrix
    for i, v_a in enumerate(shiftrows_mat):
        for j, v_b in enumerate(mix_column):
            for k, v in enumerate(v_b):

                # if xor_res has 2 elements, then we add them together using xor function
                if len(xor_res) > 3:
                    xor_mat.append(xor(xor_res))
                    xor_res = []
                # if mixColumns value = 1, then use the of shiftRows as it is

                if v == '01':
                    m = bin(int(str(v_a[k]), 16))[2:].zfill(len(str(v_a[k])) * 4)
                    xor_res.append(m)

                # if mixColumns value = 2, then use the multiply_by_2 function for calculation

                if v == '02':
                    m = multiply_by_2(v_a[k])
                    xor_res.append(m)

                # if mixColumns value = 3, then use the multiply_by_3 function for calculation

                if v == '03':
                    m = multiply_by_3(v_a[k])
                    xor_res.append(m)

                if v == '09':
                    m = multiply_by_9(v_a[k])
                    # hex to binary
                    vb = bin(int(str(v_a[k]), 16))[2:].zfill(len(str(v_a[k])) * 4)
                    m = int(vb, 2) ^ int(m, 2)
                    m = bin(m)
                    xor_res.append(m)

                if v == '0b':
                    m = multiply_by_B(v_a[k])
                    xor_res.append(m)

                if v == '0d':
                    m = multiply_by_D(v_a[k])
                    xor_res.append(m)

                if v == '0e':
                    m = multiply_by_E(v_a[k])
                    xor_res.append(m)

    xor(xor_res)
    xor_mat.append(xor(xor_res))

    return xor_mat


# sbox_ helps to convert hexa chars to letters
#
def sbox_(row, col, type):
    try:
        row = int(row)
    except ValueError:
        row = letter_to_number(row)

    try:
        col = int(col)
    except ValueError:
        col = letter_to_number(col)

    if type == 'encryption':
        return sbox(row, col)
    else:
        return sbox_inv(row, col)
