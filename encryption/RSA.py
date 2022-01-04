import random
import string
from itertools import product

import cv2 as cv
import aes_encryption as aes
import aes_decryption as aesd
import numpy as np
import json


# chars => a.encode + a.hex()
# numbers => format(a, '01x')

class AES:

    def __init__(self, photo):
        self.photo = photo
        self.b, self.g, self.r = cv.split(self.photo)

    def image_reshape(self, image):
        height, width = image.shape

        if height % 4 == 0 and width % 4 == 0:
            return image
        elif width % 4 != 0:
            missing = width - int(width / 4) * 4
            new_image = np.empty(shape=[height, width + missing], dtype=int)
            return self.image_reshape(new_image)

        elif height % 4 != 0:
            missing = height - int(height / 4) * 4
            new_image = np.empty(shape=[height + missing, width], dtype=int)
            return self.image_reshape(new_image)

    def adjustment(self, image, new_image):
        h_new_image, w_new_image = new_image.shape
        h_image, w_image = image.shape

        for i in range(0, h_image):
            new_image[i] = np.append(image[i], [255 for j in range(0, w_new_image - w_image)], axis=0)

        for i in range(1, h_new_image - h_image):
            new_image[-i] = [255 for j in range(0, w_new_image)]

        return new_image, (h_new_image, w_new_image)

    def image_slicing(self, image):
        slices = []
        height, width = image.shape

        for i in range(0, height, 4):
            for j in range(0, width, 4):
                # print('**************', (i+4, j+4))
                # print(image[i:i + 4, j:j + 4])
                slices.append(image[i:i + 4, j:j + 4])
        return slices

    def image_reconstruction(self, image_slices, keys, s, mode='enc'):
        KEYS = []  # s[0] * s[1]
        crypted_blue_c = np.empty(shape=[s[0], s[1]], dtype='<U20')
        k = 0
        for i in range(0, len(image_slices), int(s[1] / 4)):
            l = 0
            for j in range(i, i + int(s[1] / 4)):
                if mode == 'enc':
                    a = self.encrypt(image_slices[j], key)
                    crypted_blue_c[k:k + 4, l:l + 4] = a[0]
                    KEYS.append(a[1])

                if mode == 'dec':

                    ci = self.decrypt_image(image_slices[j], keys[j], key)
                        # a = self.decrypt(image_slices[j], last_k, key)
                    crypted_blue_c[k:k + 4, l:l + 4] = ci
                        # print('[OK] crypting :', 1 / len(image_slices))

                l += 4
            k += 4

        return crypted_blue_c, KEYS

    def decrypt_image(self, state, last_k, key, i=9):

        if i != -1:
            a = self.decrypt(state, last_k[i], key)
            i -= 1
            return self.decrypt_image(a, last_k, key, i)
        return state

    def crypted_image(self, hex_image, shape):

        crypted_b = np.empty(shape=[shape[0], shape[1]], dtype=int)
        crypted_g = np.empty(shape=[shape[0], shape[1]], dtype=int)
        crypted_r = np.empty(shape=[shape[0], shape[1]], dtype=int)

        for i, channel in enumerate(hex_image):
            for j, chan in enumerate(channel):
                for k, val in enumerate(chan):
                    if i == 0:
                        crypted_b[j][k] = int(channel[j][k], 16)
                    if i == 1:
                        crypted_g[j][k] = int(channel[j][k], 16)
                    if i == 2:
                        crypted_r[j][k] = int(channel[j][k], 16)

        return crypted_b, crypted_g, crypted_r

    # ##################
    # Encryption
    # ##################

    def state(self, sliced_image):
        # message
        states = []

        for i in sliced_image:
            i = i.astype('str')

            for j, v in enumerate(i):
                for k, va in enumerate(v):
                    i[j][k] = format(int(i[j][k]), '01x')
            states.append(i)

        return states

        # if len(self.message) < 16:
        #     self.message += '|' + 'Z' * (15 - len(self.message))
        #     # transform message from string to numpy matrix (state)
        #     self.message = [(l.encode('utf-8')).hex() for l in self.message]
        #
        #     self.message = np.array(self.message)
        #     self.message = np.squeeze(self.message)
        #     state_matrix = np.transpose(self.message.reshape(4, 4))
        #     return state_matrix
        # elif len(self.message) > 16:
        #     print('')
        # else:
        #     return self.message

    def generate_key(self):
        # key
        k = random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=16)
        key = []
        for char in k:
            try:
                c = int(char)
                key.append(format(c, '02x'))

            except ValueError:
                key.append((char.encode('utf-8')).hex())

        # transform key from list to numpy matrix

        key = np.array(key)
        key = np.squeeze(key)
        key = key.reshape(4, 4)
        return key

    #
    #
    #
    # # # Key
    # k = np.array([
    #     ['2b', '28', 'ab', '09'],
    #     ['7e', 'ae', 'f7', 'cf'],
    #     ['15', 'd2', '15', '4f'],
    #     ['16', 'a6', '88', '3c'],
    # ], dtype='<U20')

    #
    # # State
    #
    # a = np.array([
    #     ['32', '88', '31', 'e0'],
    #     ['43', '5a', '31', '37'],
    #     ['f6', '30', '98', '07'],
    #     ['a8', '8d', 'a2', '34'],
    # ], dtype='<U20')

    def encrypt(self, state, key):

        add_round_key_state = aes.add_round_key(state, key)

        #
        crypted = aes.main_rounds(add_round_key_state, key, 0)

        keys = aes.write_data()
        return crypted, keys

    def decrypt(self, crypted_matrix, last_key, original_key):

        # expanded_key = key_expansion(k, 9)
        add_round_key_state = aesd.add_round_key(crypted_matrix, last_key)

        shiftrows_matrix = aesd.shift_row(add_round_key_state, 'decrypt')

        subbytes_matrix = aesd.sub_bytes(shiftrows_matrix, 'decrypt')

        l = aesd.main_rounds(subbytes_matrix, 0)

        original = aesd.add_round_key(l, original_key)

        return original

    def plain_message(self, state_matrix):

        # resore orginal

        state_matrix = np.transpose(state_matrix)
        state_matrix = state_matrix.flatten()

        orginal_message = []
        for i in state_matrix:
            orginal_message.append(bytearray.fromhex(i).decode())

        return (''.join(orginal_message)).split('|')[0]


# cr = AES('127 256 0 1 5')
# state = cr.state()
# key = cr.generate_key()
#
# crypted, keys = cr.encrypt(state, key)
# # orginal_message.append(str(int(i, 16)))
# print('state')
# print(state)
#
# print('crypted')
#
# print(crypted)
#
# decrypt = cr.decrypt(crypted, keys[9], key)
#
# print('decrypted')
#
# print(decrypt)
#
# plain_text = cr.plain_message(decrypt)
#
# print('plain text')
#
# print(plain_text)


# #################
#   Encryption
# ##################


img = cv.imread("../profile.jpeg")
c = AES(img)
# gen key
key = c.generate_key()

image_b = c.b
image_g = c.g
image_r = c.r

image = [image_b, image_g, image_r]
hex_image = []
# change the image shape
new_image = c.image_reshape(image_b)
keys_b = []
keys_g = []
keys_r = []


def image_encryption_process(image, i):
    # adjust the image to the new shape
    # returns new image w ith new shape
    adjusted_image = c.adjustment(image, new_image)

    # slicing image into states
    sliced_img = c.image_slicing(adjusted_image[0])

    # crate the states
    states = c.state(sliced_img)

    # crypte the states

    crypted_imgs = c.image_reconstruction(states, key, adjusted_image[1])

    if i == 0:
        keys_b.append(crypted_imgs[1])
    if i == 1:
        keys_g.append(crypted_imgs[1])
    if i == 2:
        keys_r.append(crypted_imgs[1])

    hex_image.append(crypted_imgs[0])
    return adjusted_image[1]


for i, v in enumerate(image):
    image_shape = image_encryption_process(v, i)

# print(keys_b[0])  # key expansion
# print(keys_g[0])
# print(keys_r[0][1])

crypted_image = c.crypted_image(hex_image, image_shape)

i = cv.merge((crypted_image[0], crypted_image[1], crypted_image[2]))
cv.imwrite('ci.png', i)




# ################
#   Decryption
# ################


img = cv.imread("ci.png")
c = AES(img)

image_b = c.b
image_g = c.g
image_r = c.r

keys = [keys_b, keys_g, keys_r]

image = [image_b, image_g, image_r]

original_image = []


# change the image shape


def image_decryption_process(image, keys):
    # adjust the image to the new shape
    # returns new image w ith new shape
    # slicing image into states
    sliced_img = c.image_slicing(image)

    # crate the states
    states = c.state(sliced_img)

    # crypte the states

    crypted_imgs = c.image_reconstruction(states, keys, image.shape, mode='dec')
    original_image.append(crypted_imgs)
    return image.shape


for i, v in enumerate(image):
    image_shape = image_decryption_process(v, keys[i][0])
    if i == 0:
        print('blue channel')
    if i == 1:
        print('green channel')
    if i == 2:
        print('red channel')

origin_image = c.crypted_image(hex_image, image_shape)

i = cv.merge((origin_image[0], origin_image[1], origin_image[2]))
cv.imwrite('uci.png', i)
