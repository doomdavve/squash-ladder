#!/usr/bin/python

import argparse
import unicodecsv
import datetime
import json
import pyexcel
import re
import urllib
import urllib2

rounds_per_season = 6

def make_division_name(args, i):
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
                    newresult[0] = 'W'
                    newresult[1] = 0
                elif (result[2] == 0 and result[3] == -3):
                    newresult[0] = 0
                    newresult[1] = 'W'
                else:
                    newresult[0] = result[2]
                    newresult[1] = result[3]

                if newresult[0] == match[2] and newresult[1] == match[3]:
                    print "Up-to-date: {} - {}: {} - {}.".format(match[0].encode('utf-8'),
                                                                 match[1].encode('utf-8'),
                                                                 match[2], match[3])
                elif (newresult[0] == 'W' and newresult[1] == '0'):
                    print "Would set WO win for player one {}".format(match[0].encode('utf-8'))
                elif (newresult[0] == '0' and newresult[1] == 'W'):
                    print "Would set WO win for player two {}".format(match[1].encode('utf-8'))
                else:
                    print "Would set between {} and {} to result {} - {}. (Was {} - {})".format(match[0].encode('utf-8'),
                                                                                                match[1].encode('utf-8'),
                                                                                                newresult[0], newresult[1],
                                                                                                match[2], match[3])
                break

def main_new(args, current_book, new_book, i, ctx):
    league = "L"+str(i)
    division_name = make_division_name(args, i)
    url = "{}/load.cgi?division={}".format(args.url, division_name)
    response = urllib2.urlopen(url)
    d = json.load(response)
    if d[0] == '':
        if (args.describe):
            print "NOT IMPLEMENTED"
            print json.dumps(extract_matches(current_book, league))
            exit(2)
        else:
            values = { 'division' : division_name,
                       'data' : json.dumps(extract_matches(current_book, league)) }
            data = urllib.urlencode(values)
            req = urllib2.Request("{}/save.cgi".format(args.url), data)
            response = urllib2.urlopen(req)
            print "Saved %s: %r" % (division_name, json.loads(response.read()))
    else:
        print "Warning: can't create already existing division {}".format(division_name)

def main_update(args, current_book, new_book, i, ctx):
    league = "L"+str(i)
    division_name = make_division_name(i)
    url = "{}/load.cgi?division={}".format(args.url, division_name)
    response = urllib2.urlopen(url)
    d = json.load(response)
    if d[0] != '':
        if (args.describe):
            walk_and_describe_updates(d[4], extract_results(new_book, league))
        else:
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

def main_reset(args, current_book, new_book, i, ctx):
    league = "L"+str(i)
    division_name = make_division_name(i)
    url = "{}/load.cgi?division={}".format(args.url, division_name)
    print "Loading URL {}".format(url)
    response = urllib2.urlopen(url)
    d = json.load(response)
    if d[0] != '':
        changed = walk_and_reset(d[4], extract_results(new_book, league))
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

def init_export(args, current_book, new_book, ctx):
    fn = "{}-{}-{:02d}.csv".format(args.prefix, args.season, args.round)
    print "Writing results to {}".format(fn)
    ctx["out"] = open(fn, 'wb')
    ctx["writer"] = unicodecsv.writer(ctx["out"])
    ctx["writer"].writerow(["season","round","division","date","time","court","player1","player2","result1","result2"])

def main_export(args, current_book, new_book, i, ctx):
    league = "L"+str(i)
    matches = extract_matches(current_book, league)['games']
    for result in extract_results(new_book, league):
        m = None
        for match in matches:
            if match[0] == result[0] and match[1] == result[1]:
                m = match
                break
        outresult = [args.season, args.round, i]
        if (m):
            outresult.extend(m[4:])
        else:
            raise Exception("Couldn't find match for result {}".format(result))
        outresult.extend(result)
        ctx["writer"].writerow(outresult)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True, type=str)
    parser.add_argument("--round", required=True, type=int)
    parser.add_argument("--current-file", required=True, type=str)
    parser.add_argument("--new-file", required=True, type=str)
    subparsers = parser.add_subparsers()

    parser_new = subparsers.add_parser('new')
    parser_new.set_defaults(func=main_new)
    parser_new.add_argument("--describe", action='store_true')
    parser_new.add_argument("--url", required=True)

    parser_update = subparsers.add_parser('update')
    parser_update.set_defaults(func=main_update)
    parser_update.add_argument("--describe", action='store_true')
    parser_update.add_argument("--url", required=True)

    parser_reset = subparsers.add_parser('reset')
    parser_reset.set_defaults(func=main_reset)
    parser_reset.add_argument("--url", required=True)

    parser_export = subparsers.add_parser('export')
    parser_export.add_argument("--prefix", required=True)
    parser_export.set_defaults(init=init_export)
    parser_export.set_defaults(func=main_export)

    args = parser.parse_args()

    ctx = {}

    print "Reading from {}".format(args.current_file)
    current_book = pyexcel.get_book(file_name=args.current_file)
    print "Reading from {}".format(args.new_file)
    new_book = pyexcel.get_book(file_name=args.new_file)

    if hasattr(args, 'init'):
        args.init(args, current_book, new_book, ctx)
    for i in range(1,25):
        args.func(args, current_book, new_book, i, ctx)

if __name__ == "__main__":
    main()

