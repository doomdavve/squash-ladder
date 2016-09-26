
import os
import re

def divisions(args):
    d = sorted(os.listdir(os.path.abspath(os.path.join(args.data, 'divisions'))))
    return filter(lambda x: re.match(r'^\d\d\d\d-\d\d\d\d-\d\d-\d\d$', x), d)
