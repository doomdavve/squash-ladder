#!/usr/bin/python

import BaseHTTPServer
import CGIHTTPServer
import cgitb; cgitb.enable()  ## This line enables CGI error reporting
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--datadir", help="Path to data directory.")
args = parser.parse_args()

os.environ["DATADIR"] = "data"
if "datadir" in args:
    os.environ["DATADIR"] = args.datadir

server = BaseHTTPServer.HTTPServer
handler = CGIHTTPServer.CGIHTTPRequestHandler
server_address = ("", 9879)
handler.cgi_directories = ["/"]

httpd = server(server_address, handler)
httpd.serve_forever()
