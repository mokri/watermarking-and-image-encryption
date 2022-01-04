import json

from keyExpansion import key_expansion
from utils import sub_bytes, shift_row, mix_columns, add_round_key

# ###############################################
#               ENCRYPTION
# ##############################################


# ##########
# SubBytes
# ##########

# the subByte function is imported frm helpers file.
# we put it there to use it in key expansion, which is used in this file


# ##########
# Mix Columns
# ##########


# ##########
# Add Round Key
# ##########


AES = {}


# ##########
# Main Rounds
# ##########

def main_rounds(state, round_key, round):
    # do 9 rounds

    if round != 10:
        subbytes_matrix = sub_bytes(state)

        shiftrows_matrix = shift_row(subbytes_matrix)

        # in the last round we skip mix columns
        if round != 9:
            mixcolumns_matrix = mix_columns(shiftrows_matrix)
        else:
            mixcolumns_matrix = shiftrows_matrix

        expanded_key = key_expansion(round_key, round)

        output_matrix = add_round_key(mixcolumns_matrix, expanded_key)

        AES[round] = {
            'subByte': subbytes_matrix,
            'shiftRow': shiftrows_matrix,
            'MixColumn': mixcolumns_matrix,
            'Key': expanded_key,
            'output': output_matrix
        }
        # recursive function in each call we increment the number of rounds
        return main_rounds(output_matrix, expanded_key, round + 1)
    else:
        return state


def write_data():
    A = {}
    j = 0

    for i in AES.items():
        A[j] = i[1]['Key'].tolist()
        j += 1

    with open('output.json', 'w') as outfile:
        json.dump(A, outfile, indent=2)

    return A
