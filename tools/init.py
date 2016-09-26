#!/usr/bin/python

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--datadir", help="Path to data directory.")
args = parser.parse_args()

os.mkdir(args.datadir)
os.mkdir(os.path.join(args.datadir, "objects"))
os.mkdir(os.path.join(args.datadir, "divisions"))
