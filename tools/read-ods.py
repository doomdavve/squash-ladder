#!/usr/bin/python

import argparse
import json
import pyexcel
import urllib
import urllib2
import re
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--season", required=True)
parser.add_argument("--round", required=True, type=int)
parser.add_argument("--url", required=True)
parser.add_argument("--new", action='store_true')
parser.add_argument("--update", action='store_true')
parser.add_argument("--describe", action='store_true')
parser.add_argument("--reset", action='store_true')
args = parser.parse_args()

rounds_per_season = 6

def make_division_name(i):
    return "%s-%02d-%02d" % (args.season, args.round, i)

def parse_res(res):
    if isinstance(res, int):
        return res
    else:
        return 0

def get_result(sheet, i):
    """ get result of match between 1 and 15 (end-inclusive) """

    offset = 2
    player1name = sheet["B"+str(i+offset)]
    player2name = sheet["C"+str(i+offset)]

    player1res = parse_res(sheet["D"+str(i+offset)])
    player2res = parse_res(sheet["E"+str(i+offset)])

    return [player1name, player2name, player1res, player2res]

def get_unplayed_match(sheet, i, players):
    offset = 2

    hp = sheet["K"+str(i+offset)]
    ap = sheet["M"+str(i+offset)]
    gamedate = sheet["N"+str(i+offset)].isoformat()
    gametime = sheet["O"+str(i+offset)].strftime("%H:%M")
    gamecourse = sheet["P"+str(i+offset)]

    players.add(hp)
    players.add(ap)

    return [hp, ap, '-', '-', gamedate, gametime, gamecourse]

def compose_filename():
    season = args.season
    round = args.round
    if (args.update):
        round += 1
        if (round > rounds_per_season):
            round = 1
            m = re.match(r'([0-9]+)-([0-9]+)', season)
            season = str((int(m.group(1))+1)) + '-' + str((int(m.group(2))+1))
    return ("/Users/davve/Downloads/Squash_league_%s-%02d-final.ods" %
            (season, round))

def extract_matches(book, league):
    out = {}
    players = set()
    matches = []
    sheet = book.sheet_by_name(league)
    for game_n in range(1,16):
        match = get_unplayed_match(sheet, game_n, players)
        matches.append(match)
    out["games"] = matches
    out["players"] = list(players)
    return out

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
                newresult = [ '-', '-' ]
                if (result[2] == -3 and result[3] == 0):
                    newresult[0] = 3
                    newresult[1] = 'W'
                elif (result[2] == 0 and result[3] == -3):
                    newresult[0] = 'W'
                    newresult[1] = 3
                else:
                    newresult[0] = result[2]
                    newresult[1] = result[3]

                if newresult[0] != match[2] or newresult[1] != match[3]:
                    match[2] = newresult[0]
                    match[3] = newresult[1]
                    has_update = True
                break
    return has_update

def walk_and_reset(data, results):
    has_update = False
    for match in data['games']:
        if match[2] == '-' and match[3] == '-':
            continue
        print "Resetting match between {} and {}".format(match[0].encode('utf-8'), match[1].encode('utf-8'))
        match[2] = '-'
        match[3] = '-'
        has_update = True
    return has_update

def walk_and_describe_updates(data, results):
    for match in data['games']:
        for result in results:
            if result[0] == match[0] and result[1] == match[1]:
                newresult = [ '-', '-' ]
                if (result[2] == -3 and result[3] == 0):
                    newresult[0] = 3
                    newresult[1] = 'W'
                elif (result[2] == 0 and result[3] == -3):
                    newresult[0] = 'W'
                    newresult[1] = 3
                else:
                    newresult[0] = result[2]
                    newresult[1] = result[3]

                if newresult[0] == match[2] and newresult[1] == match[3]:
                    print "Up-to-date: {} - {}: {} - {}.".format(match[0].encode('utf-8'),
                                                                 match[1].encode('utf-8'),
                                                                 match[2], match[3])
                elif (newresult[0] == '3' and newresult[1] == 'W'):
                    print "Would set WO win for player one {}".format(match[0].encode('utf-8'))
                elif (newresult[0] == 'W' and newresult[1] == '3'):
                    print "Would set WO win for player two {}".format(match[1].encode('utf-8'))
                else:
                    print "Would set between {} and {} to result {} - {}. (Was {} - {})".format(match[0].encode('utf-8'),
                                                                                                match[1].encode('utf-8'),
                                                                                                newresult[0], newresult[1],
                                                                                                match[2], match[3])
                break

print "Reading from {}".format(compose_filename())
book = pyexcel.get_book(file_name=compose_filename())

for i in range(1,25):
    league = "L"+str(i)
    if (args.new):
        division_name = make_division_name(i)
        url = "{}/load.cgi?division={}".format(args.url, division_name)
        response = urllib2.urlopen(url)
        d = json.load(response)
        if d[0] == '':
            if (args.describe):
                print "NOT IMPLEMENTED"
                print json.dumps(extract_matches(book, league))
                exit(2)
            else:
                values = { 'division' : division_name,
                           'data' : json.dumps(extract_matches(book, league)) }
                data = urllib.urlencode(values)
                req = urllib2.Request("{}/save.cgi".format(args.url), data)
                response = urllib2.urlopen(req)
                print "Saved %s: %r" % (division_name, json.loads(response.read()))
        else:
            print "Can't create already existing division {}".format(division_name)
            exit(2)

    elif (args.update):
        division_name = make_division_name(i)
        url = "{}/load.cgi?division={}".format(args.url, division_name)
        response = urllib2.urlopen(url)
        d = json.load(response)
        if d[0] != '':
            if (args.describe):
                walk_and_describe_updates(d[4], extract_results(book, league))
            else:
                changed = walk_and_update_matches(d[4], extract_results(book, league))
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

    elif (args.reset):
        division_name = make_division_name(i)
        url = "{}/load.cgi?division={}".format(args.url, division_name)
        print "Loading URL {}".format(url)
        response = urllib2.urlopen(url)
        d = json.load(response)
        if d[0] != '':
            changed = walk_and_reset(d[4], extract_results(book, league))
            if (changed):
                values = { 'division' : division_name,
                           'parent' : d[0],
                           'data' : json.dumps(d[4]) }
                data = urllib.urlencode(values)
                req = urllib2.Request("{}/save.cgi".format(args.url), data)
                response = urllib2.urlopen(req)
                print "Updated: %s" % response.read().strip()
        else:
            print "Not implemented"
            exit(2)
