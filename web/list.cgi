#!/usr/bin/python

import cgi
import os
import json
import sys
import re

print "Content-type: application/json"
print "\n\n"

regex = re.compile(r'\d+-\d+-\d+-\d+')
divisions = filter(lambda x: re.match(regex, x), os.listdir("../data/divisions"))
divisions.sort()
json.dump(divisions, sys.stdout)
