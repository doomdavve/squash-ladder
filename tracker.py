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

def compare_match(division, matches_head, matches_tail):
    new_matches = []
    updated_matches = []

    for i, match in enumerate(matches_head):
        oldmatch = matches_tail[i]
        if match != matches_tail[i]:
            if oldmatch[2] == 0 and oldmatch[3] == 0:
                new_matches.append([match, oldmatch])
            else:
                updated_matches.append([match, oldmatch])

    if len(new_matches) > 0:
        print "{} i division {}".format(
            "Ny match" if len(new_matches) == 1 else "Nya matcher",
            division)

        for diff in new_matches:
            match = diff[0]
            oldmatch = diff[1]
            print "{} - {}: {} - {}""".format(
                match[0], match[1], match[2], match[3])

    if len(updated_matches) > 0:
        if len(new_matches) > 0:
            print

        print "{} i division {}".format(
            "Uppdaterad match" if len(updated_matches) == 1 else "Uppdaterade matcher",
            division)

        for diff in updated_matches:
            match = diff[0]
            oldmatch = diff[1]
            print "{} - {}: {} - {} ({} - {})""".format(
                match[0], match[1], match[2], match[3], oldmatch[2], oldmatch[3])

    if len(new_matches) > 0 or len(updated_matches) > 0:
        print

def object_filename(sha1):
    return os.path.abspath(os.path.join(args.data, "objects", sha1))

def walk_changes(division, new, old):
    parent = None
    olddata = None

    with gzip.open(object_filename(new), "r") as f:
        parent = f.readline().strip()
        date = f.readline().strip()
        ip = f.readline().strip()
        data = json.load(f)

    while parent != old:
        with gzip.open(object_filename(parent), "r") as f:
            parent = f.readline().strip()

    with gzip.open(object_filename(old), "r") as f:
        parent = f.readline().strip()
        olddate = f.readline().strip()
        oldip = f.readline().strip()
        olddata = json.load(f)

    compare_match(division, data["games"], olddata["games"])

# walk all divisions
divisions = os.listdir(os.path.abspath(os.path.join(args.data, "divisions")))
divisions.sort()
for division in divisions:
    f = open(os.path.abspath(os.path.join(args.data, "divisions", division)), "r")
    head = f.read()
    f.close()

    if division in known_division_state:
        old = known_division_state[division]
        if (head != old):
            walk_changes(division, head, known_division_state[division])
    else:
        print "Ny division {} hittad.".format(division)

    known_division_state[division] = head


with open(tmp_state_file, "w") as f:
    json.dump([ known_division_state ], f)

os.rename(tmp_state_file, state_file)
