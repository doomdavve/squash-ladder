#!/usr/bin/env python

import os
import re

divisions = os.listdir("data/divisions")
for division_name in divisions:
    regexp = r'(\d\d\d\d)-r(\d+)-d(\d+)'
    m = re.match(regexp, division_name)
    if m:
        oldr = m.group(2)
        if (int(oldr) < 5):
            year = "{}-{}".format((int(m.group(1)) - 1), m.group(1))
            newr = "{0:02d}".format(int(oldr)+3)
        else:
            year = "{}-{}".format((int(m.group(1))), int(m.group(1)) + 1)
            newr = "{0:02d}".format(int(oldr)-4)
        newname = "{}-{}-{}".format(year, newr, m.group(3).zfill(2))
        if not os.path.exists("data/divisions/{}".format(newname)):
            print "{} -> {}".format(division_name, newname)
            open("data/divisions/{}".format(newname), "w").write(open("data/divisions/{}".format(division_name)).read())
    else:
        print "Ignoring {}.".format(division_name)
