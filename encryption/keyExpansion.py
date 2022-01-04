from helpers import *
from utils import sub_bytes
# vector 0 generation in key expansion
def w_0(input_key, rcon, r):
    # function takes key matrix as input, and the given Rcon matrix and the round number

    # get the vector 0 from the input key matrix
    vector_0 = input_key[0]

    # get the last vector (index 3) from the input key matrix and turn it into a string
    vector_3 = ''.join([k for k in input_key[3]])

    # rotate the vector by 2
    vector_3 = vector_3[2:] + vector_3[:2]

    # restore the string from string format to list
    vector_3 = [vector_3[i:i + 2] for i in range(0, len(vector_3), 2)]

    # subByte of the vector
    vector_3 = sub_bytes(vector_3)[0]

    # rcon vector correspondent to the round number
    rcon_vector = rcon[r]

    # create an empty list to store the new values
    w = []

    # loop through vector 3, and XOR each value with it correspondent in the vector 0 and the rcon vector

    for i, j in enumerate(vector_3):
        xor_l = [

            bin(int(str(vector_0[i]), 16))[2:].zfill(len(str(vector_0[i])) * 4),
            bin(int(str(vector_3[i]), 16))[2:].zfill(len(str(vector_3[i])) * 4),
            bin(int(str(rcon_vector[i]), 16))[2:].zfill(len(str(rcon_vector[i])) * 4),
        ]
        r += 1

        # we send the values to the xor function to do the operation and we append the results to the list w

        w.append(xor(xor_l))

    return w


# the last 3 vectors generation

def w_i(input_key, key_i, i):
    w = []

    for j, v in enumerate(input_key[i]):
        xor_l = [
            bin(int(str(v), 16))[2:].zfill(len(str(v)) * 4),
            bin(int(str(key_i[i - 1][j]), 16))[2:].zfill(len(str(key_i[i - 1][j])) * 4),
        ]

        w.append(xor(xor_l))

    return w


# main expansion function


def key_expansion(input_key, r):
    # Rcon Matrix

    rcon = np.array([
        ['01', '00', '00', '00'],
        ['02', '00', '00', '00'],
        ['04', '00', '00', '00'],
        ['08', '00', '00', '00'],
        ['10', '00', '00', '00'],
        ['20', '00', '00', '00'],
        ['40', '00', '00', '00'],
        ['80', '00', '00', '00'],
        ['1b', '00', '00', '00'],
        ['36', '00', '00', '00'],
    ], dtype='<U20')

    # empty matrix to store the new key

    key_i = np.array([
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
    ], dtype='<U20')

    # we transpose the input key to treat the columns as rows

    input_key = np.transpose(input_key)

    # we pass the vector 0 to the w_0 function to generate the new vector 0

    key_i[0] = w_0(input_key, rcon, r)

    # we pass the remaining vectors to the w_i function to generate the last 3 vectors

    for i in range(1, 4):
        key_i[i] = w_i(input_key, key_i, i)

    # we transpose the returned key one more time, to it original shape
    return np.transpose(key_i)
