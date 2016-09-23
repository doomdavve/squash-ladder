#!/usr/bin/python

import cgi
import datetime
import gzip
import hashlib
import json
import os
import re
import sys

print "Content-type: application/json"
print "\n\n"

form = cgi.FieldStorage()
division = form.getvalue('division')

if (not division or not re.match(r'\d+-\d+-\d+-\d+', division)): # 2016-2017-02-12
    division = "test"

parent = "da39a3ee5e6b4b0d3255bfef95601890afd80709" # sha1 for empty string

assumedparent = form.getvalue('parent')
if (not assumedparent):
    assumedparent = parent

assumedparent.strip()

try:
    f = open(os.path.join("data", "divisions", division), "r")
    parent = f.read().strip()
    f.close()
except IOError as e:
    pass

if (parent == assumedparent and form.getvalue('data')):
    now = datetime.datetime.now().replace(microsecond=0).isoformat()
    data = form.getvalue('data')
    ip = os.environ["REMOTE_ADDR"]

    commit = '\n'.join([parent, now, ip, data])

    m = hashlib.sha1()
    m.update(commit)
    hashedname = m.hexdigest()
    dataToDisk = False

    with gzip.open(os.path.join("data", "objects", hashedname), "wb") as cf:
        cf.write(commit)

        with open(os.path.join("data", "divisions", division), "w") as hf:
            hf.write(hashedname)
            dataToDisk = True

    if (dataToDisk):
        json.dump([hashedname], sys.stdout)
    else:
        json.dump([""], sys.stdout)
else:
    json.dump([""], sys.stdout)
