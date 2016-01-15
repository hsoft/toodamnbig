# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from urllib.request import urlopen
import json
import io
import re
from tokenize import tokenize, NAME, STRING, LPAR, RPAR, LSQB, RSQB, EQUAL

from .pkg import Pkg

re_pypi_name = re.compile(r'[\w\-_]+')

def extract_requires_from_sdist(archive):
    def fail():
        raise ValueError("Can't figure out requirements")

    for name in archive.get_names():
        elems = name.split('/')
        if len(elems) == 2 and elems[1] == 'setup.py':
            setuppy = archive.read_file(name)
            break
    else:
        fail()

    tokgen = tokenize(io.BytesIO(setuppy).readline)
    # Get to 'install_require' name
    for tok in tokgen:
        if tok.type == NAME and tok.string == 'install_requires':
            break
    else:
        return set()
    if next(tokgen).exact_type != EQUAL: fail()
    if next(tokgen).exact_type not in (LSQB, LPAR): fail()
    result = set()
    # .. and then we're on for the deplist
    for tok in tokgen:
        if tok.type == NAME: fail()
        if tok.type == STRING:
            # strip the version pinning part
            # we search rathe than match because our string is quoted and we want to get
            # around that.
            pkgname = re_pypi_name.search(tok.string).group()
            result.add(PyPiPkg(pkgname))
        elif tok.exact_type in (RSQB, RPAR):
            break
    return result

def extract_requires_from_wheel(archive):
    def fail():
        raise ValueError("Can't figure out requirements")

    for name in archive.get_names():
        if name.endswith('dist-info/METADATA'):
            metadata = archive.read_file(name)
            break
    else:
        fail()

    result = set()
    for line in metadata.decode('utf-8').splitlines():
        if line.startswith('Requires-Dist: '):
            pkgname = re_pypi_name.search(line[len('Requires-Dist: '):]).group()
            result.add(PyPiPkg(pkgname))
        elif line.startswith('Provides-Extra'):
            # The following are optional deps. Let's not count them.
            break
    return result

class PyPiPkg(Pkg):
    KEEP_ARCHIVE = True # We also need the archive to get dependencies.

    def __init__(self, pkgname):
        self.name = pkgname
        with urlopen('https://pypi.python.org/pypi/{}/json'.format(pkgname)) as conn:
            self.data =  json.loads(conn.read().decode('utf-8'))

    def get_best_pkg_data(self):
        versions = {v['packagetype']: v for v in self.data['urls']}
        if 'bdist_wheel' in versions:
            return versions['bdist_wheel']
        else:
            return versions.get('sdist')

    def get_tarball_url(self):
        return self.get_best_pkg_data()['url']

    def dependencies(self):
        version = self.get_best_pkg_data()
        archive = self.get_archive()
        if version['packagetype'] == 'bdist_wheel':
            return extract_requires_from_wheel(archive)
        else:
            return extract_requires_from_sdist(archive)


