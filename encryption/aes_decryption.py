from keyExpansion import key_expansion
import numpy as np
from utils import sub_bytes, shift_row, mix_columns, add_round_key
import json

#
k_origin = np.array([
    ['74', '55', '04', '00'],
    ['00', '00', '5a', '79'],
    ['67', '06', '45', '08'],
    ['54', '79', '47', '4a'],
], dtype='<U20')


k = np.array([
    ['30', '40', '19', 'ee'],
    ['28', 'f4', '4b', '15'],
    ['06', '36', 'b3', '9a'],
    ['a1', '04', '6e', 'ee']
], dtype='<U20')

# State

state = np.array([
    ['69', 'ad', '90', 'df'],
    ['d8', '33', '3d', 'b0'],
    ['16', '71', '66', 'b8'],
    ['01', 'de', 'a2', 'ef'],
], dtype='<U20')



AES = {}


def main_rounds(state, round):
    # do 9 rounds
    with open('output.json') as f:
        data = json.load(f)

    # print(data['0'])
    # print(np.array(data['0']))
    #
    if round != 9:

        add_round_key_state = add_round_key(state, np.array(data[str(-(round+1)+9)]))

        mixcolumns_matrix = mix_columns(add_round_key_state, 'decrypt')

        shiftrows_matrix = shift_row(mixcolumns_matrix, 'decrypt')

        subbytes_matrix = sub_bytes(shiftrows_matrix, 'decrypt')

        # expanded_key = key_expansion(round_key, round)

        AES[round] = {
            'subByte': subbytes_matrix,
            'shiftRow': shiftrows_matrix,
            'MixColumn': mixcolumns_matrix,
            'Key': np.array(data[str(-(round + 1) + 9)]),
            'output': subbytes_matrix
        }

        return main_rounds(subbytes_matrix, round + 1)

    else:



        return state


#

# # expanded_key = key_expansion(k, 9)
# add_round_key_state = add_round_key(state, k)
#
# shiftrows_matrix = shift_row(add_round_key_state, 'decrypt')
#
# subbytes_matrix = sub_bytes(shiftrows_matrix, 'decrypt')
#
#
# print(subbytes_matrix)
#
# l = main_rounds(subbytes_matrix, 0)
#
# original = add_round_key(l, k_origin)
# print(original)
