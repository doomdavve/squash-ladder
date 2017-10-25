#!/usr/bin/python

import cgi
import os
import json
import sys
import re

print "Content-type: application/json"
print "\n\n"

data_dir = os.getenv("DATADIR", "../data")
divisions_dir = os.listdir(os.path.join(data_dir, "divisions"))

regex = re.compile(r'\d+-\d+-\d+-\d+')
divisions = filter(lambda x: re.match(regex, x), divisions_dir)
divisions.sort()
json.dump(divisions, sys.stdout)
