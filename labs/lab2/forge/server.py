from library import ecb_encrypt, ecb_decrypt
from library import bytes_to_text, text_to_bytes

import time
import urlparse
import json

import BaseHTTPServer

STATIC_KEY = [147, 234, 108, 117, 214, 137, 12, 174, 28, 251, 70, 20, 33, 245, 219, 205]

FLAG = 'dummy_flag'

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 5002

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        if s.path.startswith('/new_profile'):
            # Make new profile based on email parameter
            p = s.path.split("?")
            print p
            if len(p) == 1:
                s.wfile.write("<html><body><p>Please supply ?email= parameter in request</p></body></html>")
                return

            params = urlparse.parse_qs(p[1])
            print 'params', params
            if 'email' not in params:
                s.wfile.write("<html><body><p>Please supply ?email= parameter in request</p></body></html>")
                return
            else:
                email = params['email'][0]
                print 'email', email
                profile = s.profile_for(email)
                print 'profile', repr(profile)
                enc_profile = bytes_to_text(ecb_encrypt(text_to_bytes(profile), STATIC_KEY))
                print 'enc_profile', repr(enc_profile)
                s.wfile.write("<html><body>")
                s.wfile.write("<p>Profile: <span id='plain_profile'>" + profile + "</span></p>")
                s.wfile.write("<p>Encrypted: <span id='encrypted_profile'>" + enc_profile.encode('hex') + "</span></p>")
                s.wfile.write("<p><a href=\"/view_profile?encrypted_profile=" + enc_profile.encode('hex') + "\">View Profile</a></p>")
                s.wfile.write("</body></html>")
                return
        elif s.path.startswith('/view_profile'):
            p = s.path.split("?")
            if len(p) == 1:
                s.wfile.write("<html><body><p>Please access <a href=\"/new_profile\">/new_profile</a> and create a profile first.</p></body></html>")
                return
            
            params = urlparse.parse_qs(p[1])
            if 'encrypted_profile' not in params:
                s.wfile.write("<html><body><p>Please access <a href=\"/new_profile\">/new_profile</a> and create a profile first.</p></body></html>")
                return
            else:
                enc_profile = params['encrypted_profile'][0].decode('hex')
                profile = s.decrypt_parse_cookie(enc_profile)
                print 'profile', profile
                s.wfile.write("<html><body><p id=\"profile_dict\">" + json.dumps(profile) + "</p></body></html>")
                return
        elif s.path.startswith('/get_flag'):
            p = s.path.split("?")
            if len(p) == 1:
                s.wfile.write("<html><body><p>Please access <a href=\"/new_profile\">/new_profile</a> and create a profile first.</p></body></html>")
                return
            
            params = urlparse.parse_qs(p[1])
            if 'encrypted_profile' not in params:
                s.wfile.write("<html><body><p>Please access <a href=\"/new_profile\">/new_profile</a> and create a profile first.</p></body></html>")
                return
            else:
                enc_profile = params['encrypted_profile'][0].decode('hex')
                profile = s.decrypt_parse_cookie(enc_profile)
                print 'profile', profile
                if profile['role'] == 'admin':
                    s.wfile.write("<html><body><h1>Flag:</h1><p id=\"flag\">" + FLAG + "</p></body></html>")
                else:
                    s.wfile.write("<html><body><p>Sorry, you are not admin.</p></body></html>")
                return

        s.wfile.write("<html><head><title>Title goes here.</title></head>")
        s.wfile.write("<body><p>This is a test.</p>")
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("</body></html>")

    def profile_for(s, email):
        """
        >> profile_for("foobar@gmail.com")
        'email=foobar@gmail.com&uid=10&role=user
        """
        email = email.replace('&', '')
        email = email.replace('=', '')
        return "email=" + email + "&uid=10&role=user"

    def parse_cookie(s, cookie):
        return dict(urlparse.parse_qsl(cookie))

    def encrypted_profile_for(s, email):
        return ecb_encrypt(s.profile_for(email), STATIC_KEY)

    def decrypt_parse_cookie(s, enc_cookie):
        enc_cookie_bytes = text_to_bytes(enc_cookie)
        cookie_bytes = ecb_decrypt(enc_cookie_bytes, STATIC_KEY)
        cookie = bytes_to_text(cookie_bytes)
        print 'cookie string', cookie
        return s.parse_cookie(cookie)

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
