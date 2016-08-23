#!/usr/bin/python

import argparse
import os
import json
import gzip

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

known_division_state = {}

tmp_state_file = os.path.join(os.path.expanduser("~"), ".new_squash-divisions-state")
state_file = os.path.join(os.path.expanduser("~"), ".squash-divisions-state")

if (os.path.exists(state_file)):
    with open(state_file) as f:
        known_division_state = json.load(f)[0]

parser = argparse.ArgumentParser(description='Track changes.')
parser.add_argument('--data', help="Data directory")
args = parser.parse_args()

def compare_games(newgames, oldgames):
    for i, game in enumerate(newgames):
        if game != oldgames[i]:
            oldgame = oldgames[i]
            if (oldgame[2] == 0 and oldgame[3] == 0):
                print "Ny: {} vs {}: {} - {}".format(game[0], game[1], game[2], game[3])
            else:
                print "Uppdaterad: {} vs {}: {} - {}".format(game[0], game[1], game[2], game[3])
                print "            {} vs {}: {} - {}".format(oldgame[0], oldgame[1], oldgame[2], oldgame[3])

def walk_changes(new, old):
    parent = None
    olddata = None

    with gzip.open(os.path.join("data", "objects", new), "r") as f:
        parent = f.readline().strip()
        date = f.readline().strip()
        ip = f.readline().strip()
        data = json.load(f)

    while parent != old:
        with gzip.open(os.path.join("data", "objects", parent), "r") as f:
            parent = f.readline().strip()

    with gzip.open(os.path.join("data", "objects", old), "r") as f:
        parent = f.readline().strip()
        olddate = f.readline().strip()
        oldip = f.readline().strip()
        olddata = json.load(f)

    compare_games(data["games"], olddata["games"])

# walk all divisions
divisions = os.listdir(os.path.abspath(os.path.join(args.data, "divisions")))
divisions.sort()
for division in divisions:
    f = open(os.path.join("data", "divisions", division), "r")
    head = f.read()
    f.close()

    if division in known_division_state:
        old = known_division_state[division]
        if (head != old):
            walk_changes(head, known_division_state[division])
    else:
        print "Ny division {} hittad.".format(division)

    known_division_state[division] = head


with open(tmp_state_file, "w") as f:
    json.dump([ known_division_state ], f)
    print "Sparat."

os.rename(tmp_state_file, state_file)
