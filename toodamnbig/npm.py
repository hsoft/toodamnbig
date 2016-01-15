# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from urllib.request import urlopen
import json

from .pkg import Pkg

class NpmPkg(Pkg):
    def __init__(self, pkgname):
        self.name = pkgname
        with urlopen('https://registry.npmjs.org/{}'.format(pkgname)) as conn:
            self.data =  json.loads(conn.read().decode('utf-8'))
        latest_version_str = self.data['dist-tags']['latest']
        self.latest_version = self.data['versions'][latest_version_str]

    def get_tarball_url(self):
        return self.latest_version['dist']['tarball']

    def dependencies(self):
        if 'dependencies' not in self.latest_version:
            return set()
        return {NpmPkg(depname) for depname in self.latest_version['dependencies']}


