#!/usr/bin/python

import io
import os
import zipfile
import sys
import shutil

with io.BytesIO() as zip_file:
    with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED, False) as zip:
        for root, dirs, files in os.walk("data/"):
            for file in files:
                zip.write(os.path.join(root, file))

    print "Content-type: application/zip"
    print "Content-disposition: attachment; filename=database.zip"
    print "\n\n"
    sys.stdout.flush()
    sys.stdout.write(zip_file.getvalue())
