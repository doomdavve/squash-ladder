#!/usr/bin/python

import StringIO
import cgi
import csv
import gzip
import io
import json
import os
import shutil
import sys
import zipfile

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def chris_woify(r):
    if r == 'W':
        return 'WO'
    elif r == '-':
        return '0'
    else:
        return r

with cd(".."):

    form = cgi.FieldStorage()
    season = form.getvalue('season')
    round = int(form.getvalue('round'))
    format = form.getvalue('format')
    delimiter = ','

    if not format:
        format = 'default'

    if format == 'chris':
        delimiter = ';'

    output = StringIO.StringIO()
    writer = csv.writer(output, delimiter=delimiter)

    if (format == 'chris'):
        writer.writerow(["Player/Team 1","Player/Team 2","Result","Match date","Comment"])
    else:
        writer.writerow(["season","round","division","date","time","court","player1","player2","result1","result2"])

    divisions = [ "{}-{:02d}-{:02d}".format(season, round, x) for x in range(1,30)] # max is 29 divisions
    for i, division in enumerate(divisions):
        fn = os.path.join("data", "divisions", division)
        if not os.path.exists(fn):
            continue

        f = open(fn, "r")
        head = f.read()
        f.close()

        with gzip.open(os.path.join("data", "objects", head), "r") as f:
            parent = f.readline().strip()
            date = f.readline().strip()
            ip = f.readline().strip()
            data = json.load(f)
            for game in data['games']:
                if (format == 'chris'):
                    writer.writerow([
                        game[0].encode('utf-8'), game[1].encode('utf-8'),
                        "{}-{}".format(chris_woify(game[2]), chris_woify(game[3])),
                        "{} {}".format(game[4], game[5]),
                        "Bana {}".format(game[6])])
                else:
                    writer.writerow([
                        season, round, i+1, game[4], game[5], game[6],
                        game[0].encode('utf-8'), game[1].encode('utf-8'),
                        game[2], game[3]])

    sys.stdout.write("Content-type: text/csv\n")
    sys.stdout.write("Content-disposition: attachment; filename=Squash_league_results-{}-{:02d}.csv\n\n".format(season, round))
    sys.stdout.write(output.getvalue())
