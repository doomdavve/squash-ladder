#!/usr/bin/python

import io
import os
import zipfile
import sys
import shutil

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

data_dir = os.getenv("DATADIR", "../data")
with cd(data_dir):
    with io.BytesIO() as zip_file:
        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED, False) as zip:
            for root, dirs, files in os.walk("./"):
                for file in files:
                    zip.write(os.path.join(root, file))

        sys.stdout.write("Content-type: application/zip\n")
        sys.stdout.write("Content-disposition: attachment; filename=database.zip\n\n")
        sys.stdout.write(zip_file.getvalue())
