# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import re
from urllib.request import urlopen
import io
import os.path

from .tarorzip import TarOrZip

# http://stackoverflow.com/a/5989450
re_js_comment = re.compile(rb"(\/\*[\w\'\s\r\n\*]*\*\/)|(\/\/[\w\s\']*)|(\<![\-\-\s\w\>\/]*\>)")
re_c_comment = re.compile(rb"(\/\*[\w\'\s\r\n\*]*\*\/)|(\/\/[\w\s\']*)")
re_py_comment = re.compile(rb"#[^\n]*")
re_blank = re.compile(rb"\n\s*\n")

COMMENTS_RE = {
    'py': re_py_comment,
    'c': re_c_comment,
    'h': re_c_comment,
    'cpp': re_c_comment,
    'js': re_js_comment,
}


def get_sloc(contents, comment_re):
    contents = comment_re.sub(b'', contents)
    contents = re_blank.sub(b'\n', contents)
    return contents.count(b'\n')

class Pkg:
    KEEP_ARCHIVE = False

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def get_archive(self):
        if self.KEEP_ARCHIVE and hasattr(self, 'archive'):
            return self.archive
        url = self.get_tarball_url()
        if not url:
            raise ValueError("No tarball to download")
        with urlopen(url) as conn:
            tarball_bytes = conn.read()
        iszip = url.endswith('.zip') or url.endswith('.whl')
        archive = TarOrZip(io.BytesIO(tarball_bytes), iszip=iszip)
        if self.KEEP_ARCHIVE:
            self.archive = archive
        return archive

    def get_tarball_sloc(self):
        archive = self.get_archive()
        sloc = 0
        for name in archive.get_names():
            # We don't consider a file as a test if the whole package itself involves testing.
            istest = 'test' not in self.name and 'test' in name
            ext = os.path.splitext(name)[1][1:]
            issrc = ext in COMMENTS_RE
            if issrc and not istest:
                contents = archive.read_file(name)
                sloc += get_sloc(contents, comment_re=COMMENTS_RE[ext])
        return sloc


