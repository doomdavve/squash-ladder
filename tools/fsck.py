#!/usr/bin/python

import argparse
import gzip
import json
import os
import re
import hashlib

ROOT = "da39a3ee5e6b4b0d3255bfef95601890afd80709"

def walk_division(args, stats, division):
    f = open(os.path.join(args.data, "divisions", division), "r")
    head = f.read()
    stats["ndivisionrounds"]+=1
    walk_division_recursively(head, 0, stats, division)

def walk_division_recursively(obj, depth, stats, division):
    with gzip.open(os.path.join(args.data, "objects", obj), "r") as f:
        parent = f.readline().strip()
        date = f.readline().strip()
        ip = f.readline().strip()
        data = json.load(f)

        stats["nreachableobjects"]+=1
        if depth > stats["longesteditthread"]:
            stats["longesteditthread"] = depth
            stats["longesteditthread_name"] = division

        if isinstance(data, list):
            stats["oldformatobjects"]+=1

        if not parent == ROOT:
            walk_division_recursively(parent, depth + 1, stats, division)

def main(args):
    stats = {
        "oldformatobjects": 0,
        "nreachableobjects": 0,
        "ndivisionrounds": 0,
        "longesteditthread": 0,
    }
    regex = re.compile(r'\d+-\d+-\d+-\d+')
    divisions = filter(lambda x: re.match(regex, x),
                       os.listdir(os.path.join(args.data, "divisions")))
    for division in divisions:
        walk_division(args, stats, division)

    print stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--log")
    args = parser.parse_args()

    main(args)
