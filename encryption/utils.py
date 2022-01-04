import numpy as np
from helpers import sbox_, matrix_mul


# ##########
# SubBytes
# ##########

# subBytes function is used to subByte the input matrix in subByte step, and subByte of vector 0 in Key Expansion
def sub_bytes(mat, mode='encryption'):
    # empty matrix to store the subByte values

    sub_mat = np.empty((4, 4), dtype='<U20')

    # empty vector to store key expansion vector 0 subByte
    sub_vect = np.empty((1, 4), dtype='<U20')

    # test if the input is a list or matrix, and we go through it depending on its type

    if type(mat) != list:
        for row_index, row_val in enumerate(mat):
            for col_index, col_value in enumerate(row_val):
                row, col = col_value

                if len(sbox_(row, col, mode)) < 2:
                    res = '0' + sbox_(row, col, mode)
                else:
                    res = sbox_(row, col, mode)

                sub_mat[row_index][col_index] = res

        return sub_mat
    else:
        for i, val in enumerate(mat):
            row, col = val
            sub_vect[0][i] = sbox_(row, col, mode)
        return sub_vect


# ##########
# ShiftRows
# ##########

def shift_row(subbytes_mat, mode='encryption'):
    # we created an empty matrix 4x4 to store the results

    shiftrows_mat = np.empty((4, 4), dtype='<U20')

    for i, v in enumerate(subbytes_mat):

        # rotation start from index 1, i.e we skip the first row (index 0)

        if i > 0:
            # get the values from the subBytes numpy matrix and turn it into a list
            row_vals = [j for j in v]

            # we rotate the row by it index, i.e if index = 1 we rotate by 1 and so on
            if mode == 'encryption':
                row_vals = row_vals[i:] + row_vals[:i]
            else:
                row_vals = row_vals[-i:] + row_vals[:-i]

            # we restore the row from list to numpy array, and then add it to the matrix we created above(shiftrows_mat)
            shiftrows_mat[i] = np.asarray(row_vals)
        else:
            # if the index = 0, we keep the row as it is
            shiftrows_mat[i] = v

    return shiftrows_mat


def mix_columns(shiftrows_mat, mode='encryption'):
    # mix column and mix column inv are constants matrices we use theme in mix columns process

    mix_column = np.array([
        ['02', '03', '01', '01'],
        ['01', '02', '03', '01'],
        ['01', '01', '02', '03'],
        ['03', '01', '01', '02'],
    ], dtype='<U20')

    # mix column inv is used in the decryption process

    mix_column_inv = np.array([
        ['0e', '0b', '0d', '09'],
        ['09', '0e', '0b', '0d'],
        ['0d', '09', '0e', '0b'],
        ['0b', '0d', '09', '0e'],
    ], dtype='<U20')

    # we created an empty matrix 4x4 to store the results

    mul_mat = np.array([
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
        ['00', '00', '00', '00'],
    ], dtype='<U20')

    # we send the shift rows and mix columns matrices to helper function matrix mul
    # we transpose the matrix just to treat the columns as rows (simpler)

    if mode == 'encryption':
        mat = matrix_mul(np.transpose(shiftrows_mat), mix_column)
    else:
        mat = matrix_mul(np.transpose(shiftrows_mat), mix_column_inv)
    # the matrix_mul function returns a list, so we do the following to turn it into a matrix
    mat_index = 0
    for i in range(0, 4):
        for j in range(0, 4):
            mul_mat[i][j] = mat[mat_index]
            mat_index += 1
    # we transpose again the matrix to restore it to it original shape
    return np.transpose(mul_mat)


def add_round_key(mat, input_key):
    # we created an empty matrix 4x4 to store the results
    xor_mat = np.empty((4, 4), dtype='<U20')

    # we make a XOR operation
    # for each value in the input matrix, we xor it with the correspondent value in the key matrix
    # to achieve this we need to convert the matrices values which are represented as strings.
    # the process is
    for row_index, row_val in enumerate(mat):
        for col_index, col_val in enumerate(row_val):
            mat_val = col_val
            mat_key = input_key[row_index][col_index]

            xor = int(mat_val, 16) ^ int(mat_key, 16)
            xor = format(xor, '02x')

            xor_mat[row_index][col_index] = xor

    return xor_mat
