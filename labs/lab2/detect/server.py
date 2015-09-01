#!/usr/bin/env python

import SocketServer
import BaseHTTPServer
import random
import json

from flask import Flask, request, session
app = Flask(__name__)

import hashlib

from library import base64_to_bytes, bytes_to_text, bytes_to_base64, text_to_bytes
from library import ecb_encrypt, cbc_encrypt

from Crypto.Cipher import AES

FLAG = 'youre_a_hairy_wizard'

NUM_REQUIRED = 8

def gen_random_array(length):
    return [random.randint(0, 255) for i in xrange(length)]

class ChallengeManager:
    def __init__(self):
        pass

    @staticmethod
    def new_challenge(data):
        data = text_to_bytes(data)
        print 'data', data
        challenge_id = random.randint(1, 0xFFFFFFFF)
        encryption_method = random.choice(["ECB", "CBC"])
        encryptor = {
            "ECB": ChallengeManager.random_ecb,
            "CBC": ChallengeManager.random_cbc
        }[encryption_method]
        ciphertext = encryptor(
            gen_random_array(random.randint(5, 10)) + \
            data + \
            gen_random_array(random.randint(5, 10))
        )
        return {
            "data": data,
            "ciphertext": ciphertext,
            "method": encryption_method,
            "challenge_id": challenge_id,
        }

    @staticmethod
    def random_ecb(buf):
        key = gen_random_array(16)
        return ecb_encrypt(buf, key)

    @staticmethod
    def random_cbc(buf):
        key = gen_random_array(16)
        iv = gen_random_array(16)
        return cbc_encrypt(buf, key, iv)
        

@app.route("/")
def web_root():
    return "Hi!"
    pass

@app.route("/new_challenge")
def web_new_challenge():
    if 'data' not in request.args:
        return "<html><body><p>Please supply ?data= hex-encoded parameter in request</p></body></html>"
    data_hex = request.args.get('data', '')
    data = ''
    try:
        data = data_hex.decode('hex')
    except TypeError, e:
        return "<html><body><p>Could not understand ?data= parameter: " + e.message + "</p></body></html>"

    # verify the user does not already have a challenge out
    if 'challenge' in session:
        # Clear away the history
        session['num_correct'] = 0

    chal = ChallengeManager.new_challenge(data)
    session['challenge'] = chal
    html = "<html><body>"
    html += "<p>Data: <span id=\"data\">" + repr(chal['data']) + "</span></p>" + "\n"
    html += "<p>Ciphertext: <span id=\"ciphertext\">" + repr(chal['ciphertext']) + "</span></p>" + "\n"
    html += "<p>Challenge Id: <span id=\"challenge_id\">" + repr(chal['challenge_id']) + "</span></p>" + "\n"
    html += "<p>Method: <span id=\"method\">" + repr(chal['method']) + "</span></p>" + "\n"
    html += "</body></html>"
    return html

@app.route("/solve_challenge")
def web_solve_challenge():
    try:
        request.args['challenge_id']
        request.args['guess']
    except KeyError:
        return "<html><body><p>You need to supply ?challenge_id= and &guess= in the URL</p></body></html>"

    # Fun fact: We don't use challenge_id at all, but I want to keep it.
    challenge_id = int(request.args['challenge_id'])
    guess = request.args['guess']

    # Get the most recent challenge
    try:
        chal = session['challenge']
        del session['challenge']
    except KeyError:
        return "<html><body><p>Go get a challenge at /new_challenge</p></body></html>"

    if guess not in ["ECB", "CBC"]:
        return "<html><body><p>Guess should be one of [ECB, CBC]</p></body></html>"

    if guess == chal['method']:
        session['num_correct'] = 1 + session.get('num_correct', 0)
        correct_str = "Correct!"
    else:
        session['num_correct'] = 0
        correct_str = "Incorrect."

    if session['num_correct'] >= NUM_REQUIRED:
        return "<html><body><p id=\"result\">%s</p><p id=\"Progress\"><span id=\"num_correct\">%d</span> in a row correct.</p><p id=\"flag\">Flag: %s</p></body></html>" % (correct_str, session['num_correct'], FLAG)
    else:
        return "<html><body><p id=\"result\">%s</p><p id=\"Progress\"><span id=\"num_correct\">%d</span> in a row correct.</p></body></html>" % (correct_str, session['num_correct'],)

if __name__ == '__main__':
    app.secret_key = '\x97"r\xa7d0\xc8\xf9\xa7\xf7y\xb9\x8a\xe6\xa83\xb5s\x16\x07\xcdm\x9f\xed'
    app.run(debug=True)
