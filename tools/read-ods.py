#!/usr/bin/python

import argparse
import unicodecsv
import datetime
import json
import pyexcel
import re
import urllib
import urllib2

def make_division_name(args, i):
    return "%s-%02d-%02d" % (args.season, args.round, i)

def parse_res(res):
    if isinstance(res, int):
        return res
    else:
        return 0

def get_result(sheet, i):
    """ get result of match between 1 and 15 (end-inclusive) """
    offset = 3
    row = (i + offset) + ((i-1) / 3)

    player1name = sheet["B"+str(row)].strip()
    player2name = sheet["C"+str(row)].strip()
    player1res = parse_res(sheet["D"+str(row)])
    player2res = parse_res(sheet["E"+str(row)])
    if player1name == '' or player2name == '':
        print "ERROR: at match " + i
        exit(2)
    return [player1name, player2name, player1res, player2res]

def extract_results(book, league):
    results = []
    sheet = book.sheet_by_name(league)
    for game_n in range(1,16):
        results.append(get_result(sheet, game_n))
    return results

def walk_and_update_matches(data, results):
    has_update = False
    for match in data['games']:
        for result in results:
            if result[0] == match[0] and result[1] == match[1]:
                newresult = [ '0', '0' ]
                if (result[2] == -3 and result[3] == 0):
                    newresult[0] = 'W'
                    newresult[1] = 0
                elif (result[2] == 0 and result[3] == -3):
                    newresult[0] = 0
                    newresult[1] = 'W'
                else:
                    newresult[0] = result[2]
                    newresult[1] = result[3]

                if newresult[0] != match[2] or newresult[1] != match[3]:
                    match[2] = newresult[0]
                    match[3] = newresult[1]
                    has_update = True
                break
    return has_update

def main_update(args, new_book, i):
    league = "L"+str(i)
    division_name = make_division_name(args, i)
    url = "{}/load.cgi?division={}".format(args.url, division_name)
    response = urllib2.urlopen(url)
    d = json.load(response)
    if d[0] != '':
        changed = walk_and_update_matches(d[4], extract_results(new_book, league))
        if (changed):
            values = { 'division' : division_name,
                       'parent' : d[0],
                       'data' : json.dumps(d[4]) }
            data = urllib.urlencode(values)
            req = urllib2.Request("{}/save.cgi".format(args.url), data)
            response = urllib2.urlopen(req)
            print "Updated: %s" % response.read().strip()
        else:
            print "No change: {}".format(division_name)
    else:
        print "Can't update non existing division {}".format(division_name)
        exit(2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--divisions", required=True, type=int)
    parser.add_argument("--season", required=True, type=str)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--file", required=True, type=str)
    parser.add_argument("--url", required=True)
    parser.set_defaults(func=main_update)
    args = parser.parse_args()

    print "Reading from {}".format(args.file)
    new_book = pyexcel.get_book(file_name=args.file)
    for i in range(1, args.divisions+1):
        args.func(args, new_book, i)

if __name__ == "__main__":
    main()

