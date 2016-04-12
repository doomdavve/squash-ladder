#!/usr/bin/python

import cgi
import gzip
import hashlib
import json
import os
import sys

print "Content-type: application/json"
print "\n\n"

form = cgi.FieldStorage()
division = form.getvalue('division')
if (not division):
    division = "test"

try:
    f = open(os.path.join("data", "divisions", division), "r")
    head = f.read()
    f.close()

    f = gzip.open(os.path.join("data", "objects", head), "r")
    parent = f.readline().strip()
    date = f.readline().strip()
    ip = f.readline().strip()
    data = f.read()
    f.close()

    json.dump([head, parent, date, ip, data], sys.stdout)
except IOError as e:
    json.dump([""], sys.stdout)
