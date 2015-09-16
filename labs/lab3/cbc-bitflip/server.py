#!/usr/bin/env python

import SocketServer
import BaseHTTPServer
import random
import json

from flask import Flask, request, session, url_for
app = Flask(__name__)

import hashlib

from library import base64_to_bytes, bytes_to_text, bytes_to_base64, text_to_bytes
from library import cbc_encrypt, cbc_decrypt

from Crypto.Cipher import AES

FLAG = 'dummy_flag'
NUM_REQUIRED = 8
STATIC_KEY = range(16)

PORT = 5031


def gen_random_array(length):
    return [random.randint(0, 255) for i in xrange(length)]

def bake_cookie(userdata):
    iv = gen_random_array(16)
    cookie = "comment1=cooking%20MCs;userdata=" + \
        userdata.replace(';', '').replace('=', '') + \
        ";comment2=%20like%20a%20pound%20of%20bacon"
    baked_cookie = cbc_encrypt(cookie, STATIC_KEY, iv)
    return bytes_to_text(iv), baked_cookie

def enjoy_cookie(iv, baked_cookie):
    assert len(iv) == 16
    
    iv = text_to_bytes(iv)
    cookie = cbc_decrypt(baked_cookie, STATIC_KEY, iv)
    print 'cookie', repr(cookie)
    return ';admin=true;' in cookie

"""
Decrypt cookie
"""
def review_cookie(iv, baked_cookie):
    assert len(iv) == 16
    
    iv = text_to_bytes(iv)
    cookie = cbc_decrypt(baked_cookie, STATIC_KEY, iv)
    print 'cookie', repr(cookie)
    return cookie


@app.route("/update_userdata")
def update_userdata():
    html = "<html><body>"
    if 'userdata' in request.args:
        userdata_hex = request.args.get('userdata', '')
        userdata = ''
        try:
            userdata = userdata_hex.decode('hex')
        except TypeError, e:
            return "<html><body><p>Could not understand ?userdata= parameter: " + e.message + "</p></body></html>"

        iv, cookie = bake_cookie(userdata)
        html += "<p><pre>Cookie: <span id='cookie'>" + cookie.encode('hex') + "</span></pre></p>" + "\n"
        html += "<p><pre>IV: <span id='iv'>" + iv.encode('hex') + "</span></pre></p>" + "\n"
        html += "<p><a href=\"" + url_for('get_flag') + '?cookie=' + cookie.encode('hex') + '&iv=' + iv.encode('hex') + '">Try to access flag</a></p>' + "\n"

    html += "<h1>Update Userdata</h1>"
    html += "<form method=\"get\">"
    html += "Userdata: <input type=\"text\" name=\"userdata\" />"
    html += "</form>"
    html += "</body></html>"
    return html

@app.route("/get_flag")
def get_flag():
    try:
        request.args['cookie']
    except KeyError:
        return "<html><body><p>You need to supply ?cookie= in the URL</p></body></html>"

    cookie_hex = request.args['cookie']
    cookie = cookie_hex.decode('hex')
    iv_hex = request.args['iv']
    iv = iv_hex.decode('hex')

    if enjoy_cookie(iv, cookie):
        return '<html><body><p>That was delicious! Have a flag: <span id="flag">' + FLAG + '</span></p></body></html>'
    else:
        html = ''
        html += '<html><body>'
        html += '<p>That tasted terrible!</p>'
        html += '<p>Decrypted: <pre><span id="decrypted_data">' + review_cookie(iv, cookie) + '</span></pre></p>'
        html += 'Cookie does not contain ";admin=true;"'
        html += '</body></html>'
        return html

if __name__ == '__main__':
    app.secret_key = '0123456789012345678901234567890'
    app.run('0.0.0.0', PORT, debug=True)
