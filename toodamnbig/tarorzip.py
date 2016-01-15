# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import tarfile
import zipfile

class TarOrZip:
    """Just a simple common interface over tarfile and zipfile.
    """
    def __init__(self, fileobj, iszip=False):
        self.iszip = iszip
        if self.iszip:
            self.archive = zipfile.ZipFile(fileobj)
        else:
            self.archive = tarfile.open(fileobj=fileobj)

    def get_names(self):
        if self.iszip:
            return self.archive.namelist()
        else:
            return self.archive.getnames()

    def read_file(self, name):
        if self.iszip:
            return self.archive.read(name)
        else:
            return self.archive.extractfile(name).read()

