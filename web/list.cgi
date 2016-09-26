#!/usr/bin/python

import cgi
import os
import json
import sys

print "Content-type: application/json"
print "\n\n"

divisions = os.listdir("../data/divisions")
divisions.sort()
json.dump(divisions, sys.stdout)
