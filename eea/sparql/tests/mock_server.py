""" Mock http server for testing sparql"""

from __future__ import print_function
from random import randint
import six.moves.BaseHTTPServer
import sys
import os

PORT = randint(17000, 19000)

class Handler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    """ Mock http request handler"""

    def do_POST(self):
        """ On post return the contents of sparql.xml file"""
        self.send_response(200)
        self.send_header("Content-type", "application/sparql-results+json")
        self.end_headers()
        stdout = sys.stdout
        sys.stdout = self.wfile
        json_file = os.path.join(os.path.dirname(__file__), "sparql.xml")
        f = open(json_file, 'rb')
        json_str = f.read()
        f.close()
        # import pdb; pdb.set_trace()
        sys.stdout.write(json_str)
        # print(json_str, file=sys.stdout)
        sys.stdout = stdout

    def do_GET(self):
        """ GET"""
        return self.do_POST()

if __name__ == "__main__":
    httpd = six.moves.BaseHTTPServer.HTTPServer(("", PORT), Handler)
    httpd.serve_forever()
