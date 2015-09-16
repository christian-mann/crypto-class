#!/usr/bin/env python

import SocketServer
import BaseHTTPServer
import random
import json

from flask import Flask, request, session, url_for
app = Flask(__name__)

import hashlib

from library import base64_to_bytes, bytes_to_text, bytes_to_base64, text_to_bytes
from library import cbc_encrypt, cbc_decrypt, PaddingError

from Crypto.Cipher import AES

FLAG = 'dummy_flag_padding_padding_padding_padding'
NUM_REQUIRED = 8
STATIC_KEY = range(16)

PORT = 5032


def gen_random_array(length):
    return [random.randint(0, 255) for i in xrange(length)]

def encrypted_message_oracle():
    current_iv = gen_random_array(16)
    # It's annoying to decrypt the first block, since it involves messing with the IV.
    # You're welcome to try if you want, but you do not have to.
    message = 'A'*16 + FLAG
    ciphertext = cbc_encrypt(message, STATIC_KEY, current_iv)
    return (ciphertext, current_iv)

def padding_oracle(ciphertext, iv):
    assert len(iv) == 16
    try:
        plaintext = cbc_decrypt(ciphertext, STATIC_KEY, iv)
        return True
    except PaddingError:
        return False

@app.route("/get_ciphertext")
def get_ciphertext():
    html = "<html><body>" + "\n"
    ciphertext, iv = encrypted_message_oracle()
    iv = bytes_to_text(iv)
    html += '<p>IV: <pre><span id="iv">' + iv.encode('hex') + '</span></pre></p>' + "\n"
    html += '<p>Ciphertext: <pre><span id="ciphertext">' + ciphertext.encode('hex') + '</span></pre></p>' + "\n"
    html += '<p><a href="' + url_for('check_padding') + '?encrypted_data=' + ciphertext.encode('hex') + '&iv=' + iv.encode('hex') + '">Submit</a></p>' + "\n"
    html += '</body></html>'
    return html

@app.route("/check_padding")
def check_padding():
    html = "<html><body>"
    if 'encrypted_data' in request.args and 'iv' in request.args:
        encrypted_data_hex = request.args.get('encrypted_data', '')
        encrypted_data = ''
        try:
            encrypted_data = bytearray.fromhex(encrypted_data_hex)
        except TypeError, e:
            return "<html><body><p>Could not understand ?encrypted_data= parameter: " + e.message + "</p></body></html>"

        iv_hex = request.args.get('iv', '')
        iv = ''
        try:
            iv = bytearray.fromhex(iv_hex)
        except TypeError, e:
            return "<html><body><p>Could not understand ?iv= parameter: " + e.message + "</p></body></html>"

        good_padding = padding_oracle(encrypted_data, iv)
        html += '<p><span id="good_padding">' + str(good_padding) + '</span></p>' + "\n"
    else:
        html += '<p>You need to supply ?encrypted_data and ?iv in the URL</p>'
    html += '</body></html>'
    return html

if __name__ == '__main__':
    app.secret_key = '0123456789012345678901234567890'
    app.run('0.0.0.0', PORT, debug=True)
