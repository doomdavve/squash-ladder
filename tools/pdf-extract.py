#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import json
import math
import urllib2
import urllib

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("filename")
parser.add_argument("--season", required=True)
parser.add_argument("--round", required=True, type=int)
parser.add_argument("--url", required=True)
args = parser.parse_args()

# Open a PDF file.
fp = open(args.filename, 'rb')
parser = PDFParser(fp)
document = PDFDocument(parser)
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed
rsrcmgr = PDFResourceManager()

# BEGIN LAYOUT ANALYSIS
# Set parameters for analysis.
laparams = LAParams(
    line_overlap=0.1,
    char_margin=0.1,
    line_margin=0.5,
    word_margin=0.1,
    boxes_flow=0.5,
)

# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)

# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)

INFO_FIRST_ROW = 720
INFO_SECOND_ROW = 650
FUZZINESS = 14
FUZZINESS_X = FUZZINESS
FUZZINESS_Y = FUZZINESS

def fuzzy_match(a1, a2):
    if abs(a1[0] - a2[0]) > FUZZINESS_X or abs(a1[1] - a2[1]) > FUZZINESS_Y:
        return False
    return True

class PageState(object):
    def __init__(self):
        self.scanning_table = [
            [ "DIVISION_NR", [492, 795] ],

            [ "SPELDATUM_1", [93, 769] ],
            [ "SPELDATUM_1_REDUNDANT", [271, INFO_FIRST_ROW] ],
            [ "TID_BANA_1", [331, INFO_FIRST_ROW] ],
            [ "SPELARE_HEMMA_1", [40, INFO_FIRST_ROW] ],
            [ "SPELARE_BORTA_1", [162, INFO_FIRST_ROW] ],

            [ "SPELDATUM_2", [93, 706] ],
            [ "SPELDATUM_2_REDUNDANT", [271, INFO_SECOND_ROW] ],
            [ "TID_BANA_2", [331, INFO_SECOND_ROW] ],
            [ "SPELARE_HEMMA_2", [40, INFO_SECOND_ROW] ],
            [ "SPELARE_BORTA_2", [162, INFO_SECOND_ROW] ],

            [ "SPELDATUM_3", [93, 643] ],
            [ "SPELDATUM_3_REDUNDANT", [271, 590] ],
            [ "TID_BANA_3", [331, 590] ],
            [ "SPELARE_HEMMA_3", [40, 590] ],
            [ "SPELARE_BORTA_3", [162, 590] ],

            [ "SPELDATUM_4", [93, 580] ],
            [ "SPELDATUM_4_REDUNDANT", [271, 530] ],
            [ "TID_BANA_4", [331, 530] ],
            [ "SPELARE_HEMMA_4", [40, 530] ],
            [ "SPELARE_BORTA_4", [162, 530] ],

            [ "SPELDATUM_5", [93, 517] ],
            [ "SPELDATUM_5_REDUNDANT", [271, 470] ],
            [ "TID_BANA_5", [331, 470] ],
            [ "SPELARE_HEMMA_5", [40, 469] ],
            [ "SPELARE_BORTA_5", [162, 469] ],

            [ "SPELARE_1_NAMN", [40, 435] ],
            [ "SPELARE_1_TEL_HEM", [176, 435] ],
            [ "SPELARE_1_TEL_ARBETE", [289, 435] ],
            [ "SPELARE_1_TEL_MOBIL", [399, 435] ],

            [ "SPELARE_2_NAMN", [40, 420] ],
            [ "SPELARE_2_TEL_HEM", [176, 420] ],
            [ "SPELARE_2_TEL_ARBETE", [289, 420] ],
            [ "SPELARE_2_TEL_MOBIL", [399, 420] ],

            [ "SPELARE_3_NAMN", [40, 405] ],
            [ "SPELARE_3_TEL_HEM", [176, 405] ],
            [ "SPELARE_3_TEL_ARBETE", [289, 405] ],
            [ "SPELARE_3_TEL_MOBIL", [399, 405] ],

            [ "SPELARE_4_NAMN", [40, 390] ],
            [ "SPELARE_4_TEL_HEM", [176, 390] ],
            [ "SPELARE_4_TEL_ARBETE", [289, 390] ],
            [ "SPELARE_4_TEL_MOBIL", [399, 390] ],

            [ "SPELARE_5_NAMN", [40, 374] ],
            [ "SPELARE_5_TEL_HEM", [176, 374] ],
            [ "SPELARE_5_TEL_ARBETE", [289, 374] ],
            [ "SPELARE_5_TEL_MOBIL", [399, 374] ],

            [ "SPELARE_6_NAMN", [40, 358] ],
            [ "SPELARE_6_TEL_HEM", [176, 358] ],
            [ "SPELARE_6_TEL_ARBETE", [289, 358] ],
            [ "SPELARE_6_TEL_MOBIL", [399, 358] ],

        ]
        self.ignored_tokens = [
            "Division:",
            "Team Göteborg Squashstege",
            "Speldatum",
            "Resultat",
            "-\n-\n-",
            "Hem\n.*",
            "Arbetet\n.*",
            "Mobil.*",
            "är sista dagen.*",
            "Glöm inte att ringa.*",
            "Frågor till .*",
            "Nästa omgång spelas.*",
            "matcher.",
            "Hem",
            "Arbetet",
            "-"
        ]
        # telephone number:
        self.ignored_tokens_with_coord = [
            [ ".*", [57, 329] ], # Sista datum for uppskjutna matcher
            [ ".*", [134, 307] ], # datum
        ]
        self.scanning_results = {}

    def process_input(self, xcoord, ycoord, text):

        #print "%6d, %6d, %s" % (xcoord, ycoord, text.replace('\n', '\\n').encode('utf-8'))

        for ignored in self.ignored_tokens:
            if re.match(ignored, text.encode('utf-8')):
                #print "ignored: %s" % text.replace('\n', '\\n').encode('utf-8')
                return

        for ignored in self.ignored_tokens_with_coord:
            if re.match(ignored[0], text.encode('utf-8')) and fuzzy_match([xcoord, ycoord], ignored[1]):
                #print "ignored with coord: %s" % text.replace('\n', '\\n').encode('utf-8')
                return

        for entry in self.scanning_table:
            if fuzzy_match([xcoord, ycoord], entry[1]):
                if entry[0] in self.scanning_results:
                    raise Exception("Duplicate entry: %6d, %6d, %s with %s" % (xcoord, ycoord, text.replace('\n', '\\n').encode('utf-8'), self.scanning_results[entry[0]]))

                self.scanning_results[entry[0]] = text
                print "accepted: '%s' as %s" % (text.replace('\n', '\\n').encode('utf-8'), entry[0])
                return

        raise Exception("Unexpected text: [%d, %d]: '%s'" %
                    (xcoord, ycoord, text.replace('\n', '\\n').encode('utf-8')))

    def check_done(self):
        return 'SPELARE_BORTA_5' in self.scanning_results

    def division_name(self):
        return "{0:s}-{1:02d}-{2:02d}".format(args.season, args.round, int(self.scanning_results["DIVISION_NR"]))

    def calc_games(self):
        out = {}

        players = set()
        games = []
        for gamenr in range(1,6):
            #print gamenr
            gamedate = self.scanning_results["SPELDATUM_%d_REDUNDANT" % gamenr].split("\n")[0]
            homeplayers = self.scanning_results["SPELARE_HEMMA_%d" % gamenr].split("\n")[0:3]
            awayplayers = self.scanning_results["SPELARE_BORTA_%d" % gamenr].split("\n")[0:3]
            gameinfo = self.scanning_results["TID_BANA_%d" % gamenr].split("\n")[0:3]
            gametime = "??:??"
            gamecourse = "?"
            for i, homeplayer in enumerate(homeplayers):
                #print "* %d" % i
                hp = homeplayer.encode('utf-8')
                ap = awayplayers[i].encode('utf-8')
                m = re.match("Tid : (\d\d:\d\d), Bana : (\d)", gameinfo[i].encode('utf-8'))
                if (m):
                    gametime = m.group(1)
                    gamecourse = m.group(2)
                games.append([hp, ap, '-', '-', gamedate, gametime, gamecourse])
                players.add(hp)
                players.add(ap)

#        if len(players) != 6:
#            raise Exception("Wrong number of players: {}".format(len(players), players))

        out["games"] = games
        out["players"] = list(players)

        return out

    def __str__(self):
        return "Division %d\nSpeldatum: %s\nSpelare (v): %s, \nSpelare (h): %s, \nSpelare: %s\nTid och bana: %s" % (self.divisionnr, self.speldatum, self.leftsideplayers, self.rightsideplayers, self.players, self.timeandcourt)

def parse_obj(lt_objs, texts):

    # loop over the object list
    for obj in lt_objs:

        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            texts.append([ obj.bbox[0], obj.bbox[1], obj.get_text() ])

        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            parse_obj(obj._objs, page_state)

i = 0
# loop over all pages in the document
for i, page in enumerate(PDFPage.create_pages(document)):
    p = PageState()

    # read the page into a layout object
    interpreter.process_page(page)
    layout = device.get_result()

    texts = []

    # extract texts from this object
    parse_obj(layout._objs, texts)

    # sort text on first x, then y coordinate.
    texts.sort(key=lambda a: a[0], reverse=False)
    texts.sort(key=lambda a: a[1], reverse=True)

    try:
        for text in texts:
            p.process_input(text[0], text[1], text[2].strip())

        r = p.calc_games()
        json.dump(r, sys.stdout)
    except:
        print i
        raise

    url = "{}/load.cgi?division={}".format(args.url, p.division_name())
    print url
    response = urllib2.urlopen(url)
    data = json.load(response)

    if data[0] == '':
        values = { 'division' : p.division_name(),
                   'data' : json.dumps(r) }
        data = urllib.urlencode(values)

        req = urllib2.Request("{}/save.cgi".format(args.url), data)
        response = urllib2.urlopen(req)
        print "Saved: %s" % response.read()
