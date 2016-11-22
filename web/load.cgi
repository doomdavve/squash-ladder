#!/usr/bin/python

import cgi
import gzip
import hashlib
import json
import os
import sys
import re
import urllib

print "Content-type: application/json"
print "\n\n"

form = cgi.FieldStorage()
division = form.getvalue('division')
player = unicode(urllib.unquote(form.getvalue('player')), 'utf-8') if not division else None

division = "test" if not division else division

if player:
    division_regex = re.compile(r'\d\d\d\d-\d\d\d\d-\d\d-\d\d')
    divisions = filter(lambda x: re.match(division_regex, x), os.listdir("../data/divisions"))
    divisions.sort()

    hits = []

    for division in divisions:
        f = open(os.path.join("..", "data", "divisions", division), "r")
        head = f.read()
        f.close()

        with gzip.open(os.path.join("..", "data", "objects", head), "r") as f:
            parent = f.readline().strip()
            date = f.readline().strip()
            ip = f.readline().strip()
            data = json.load(f)

            if player in data["players"]:
                hits.append([division, data])

    json.dump([player, hits], sys.stdout)

else:
    try:
        f = open(os.path.join("..", "data", "divisions", division), "r")
        head = f.read()
        f.close()

        with gzip.open(os.path.join("..", "data", "objects", head), "r") as f:
            parent = f.readline().strip()
            date = f.readline().strip()
            ip = f.readline().strip()
            data = json.load(f)

            json.dump([head, parent, date, ip, data], sys.stdout)
    except IOError as e:
        json.dump([""], sys.stdout)
