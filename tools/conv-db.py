#!/usr/bin/python

""" "Throw-away" script to convert the database. Currently implements
# moving from old walkover score to the established (but then unknown
# to me) format. """

import argparse
import gzip
import json
import os
import re
import hashlib

ROOT = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
files_unchanged = 0
files_changed = 0
paths_truncated = 0

def convert_division(args, division):
    f = open(os.path.join(args.data, "divisions", division), "r")
    head = f.read()
    new_head = convert_division_recursively(head)

    if (new_head != head):
        with open(os.path.join(args.data, "divisions", division), "w") as hf:
            hf.write(new_head)

def convert_division_recursively(obj):
    with gzip.open(os.path.join(args.data, "objects", obj), "r") as f:
        parent = f.readline().strip()
        date = f.readline().strip()
        ip = f.readline().strip()
        data = json.load(f)

        has_change = False

        if isinstance(data, list):
            # old format; ignore these
            global paths_truncated
            paths_truncated+=1
            return ROOT
        elif not parent == ROOT:
            new_parent = convert_division_recursively(parent)
            if new_parent != parent:
                has_change = True
                parent = new_parent

        for game in data["games"]:
            if game[2] == 'W' and game[3] == 3:
                game[2] = '0'
                game[3] = 'W'
                has_change = True
            elif game[2] == 3 and game[3] == 'W':
                game[2] = 'W'
                game[3] = '0'
                has_change = True

        if has_change:
            commit = '\n'.join([parent, date, ip, json.dumps(data)])

            m = hashlib.sha1()
            m.update(commit)
            hashedname = m.hexdigest()
            dataToDisk = False

            with gzip.open(os.path.join(args.data, "objects", hashedname), "wb") as cf:
                cf.write(commit)
                dataToDisk = True

            if (dataToDisk):
                global files_changed
                files_changed+=1
                return hashedname
            else:
                raise Exception("Error writing data to disk")
        else:
            global files_unchanged
            files_unchanged+=1
            return obj

def main(args):
    regex = re.compile(r'\d+-\d+-\d+-\d+')
    divisions = filter(lambda x: re.match(regex, x),
                       os.listdir(os.path.join(args.data, "divisions")))
    for division in divisions:
        convert_division(args, division)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()

    main(args)

    print "{} file(s) changed. {} file(s) unchanged. {} change path(s) truncated".format(
        files_changed, files_unchanged, paths_truncated)

