#!/usr/bin/env python3
# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import argparse
from urllib.request import urlopen
import json
import tarfile
import io
import re

# http://stackoverflow.com/a/5989450
re_js_comment = re.compile(rb"(\/\*[\w\'\s\r\n\*]*\*\/)|(\/\/[\w\s\']*)|(\<![\-\-\s\w\>\/]*\>)")
re_blank = re.compile(rb"\n\s*\n")

def get_parser():
    parser = argparse.ArgumentParser(description='Compute how too damn big is the specified dependency')
    parser.add_argument('pkgname')
    return parser

class NpmPkg:
    def __init__(self, pkgname):
        self.name = pkgname
        with urlopen('https://registry.npmjs.org/{}'.format(pkgname)) as conn:
            self.data =  json.loads(conn.read().decode('utf-8'))
        latest_version_str = self.data['dist-tags']['latest']
        self.latest_version = self.data['versions'][latest_version_str]

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

def get_tarball_sloc(tarball_url):
    with urlopen(tarball_url) as conn:
        tarball_bytes = conn.read()
    tarball = tarfile.open(fileobj=io.BytesIO(tarball_bytes))
    sloc = 0
    for member in tarball.getmembers():
        if member.name.endswith('.js'):
            contents = tarball.extractfile(member).read()
            sloc += get_js_sloc(contents)
    return sloc

def get_js_sloc(contents):
    contents = re_js_comment.sub(b'', contents)
    contents = re_blank.sub(b'\n', contents)
    return contents.count(b'\n')

def get_flat_deps(pkg, ignore=None):
    if ignore and pkg in ignore:
        return set()
    if 'dependencies' not in pkg.latest_version:
        return set()
    result = set()
    for depname in pkg.latest_version['dependencies']:
        subpkg = NpmPkg(depname)
        result |= get_flat_deps(subpkg, ignore=result)
        result.add(subpkg)
    return result

def main():
    args = get_parser().parse_args()
    mainpkg = NpmPkg(args.pkgname)
    print("Getting dependencies...")
    deps = get_flat_deps(mainpkg)
    allpkgs = {mainpkg} | deps
    sloc = 0
    for pkg in allpkgs:
        tarball_url = pkg.latest_version['dist']['tarball']
        sloc += get_tarball_sloc(tarball_url)
    print("{:,} SLOC in {} packages needed to provide you with {}'s functionalities".format(
        sloc, len(allpkgs), mainpkg.name
    ))
    print("... not counting Node which is itself 5M SLOC")
    print("NASA flies to **space** with 400k sloc")

if __name__ == '__main__':
    main()

