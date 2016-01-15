# Copyright 2016 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import argparse
from urllib.error import HTTPError

from .npm import NpmPkg
from .pypi import PyPiPkg

BASE_REQUIREMENTS = {
    'pypi': ('Python', '1M'),
    'npm': ('Node', '5M'),
}

def get_parser():
    parser = argparse.ArgumentParser(description='Compute how too damn big is the specified dependency')
    parser.add_argument('pkgname')
    parser.add_argument('--verbose', action='store_true')
    return parser

def get_flat_deps(pkg, ignore=None, verbose=False):
    if ignore and pkg in ignore:
        return set()
    if ignore is None:
        ignore = set()
    ignore.add(pkg)
    result = set()
    try:
        deps = pkg.dependencies()
        if verbose:
            print("{}: {}".format(pkg.name, ', '.join(d.name for d in deps)))
    except ValueError:
        print("WARNING: Couldn't figure out {}'s dependencies. Skipping")
        return set()
    for subpkg in deps:
        result |= get_flat_deps(subpkg, ignore=ignore, verbose=verbose)
        result.add(subpkg)
    return result

def main():
    args = get_parser().parse_args()
    try:
        prefix, pkgname = args.pkgname.split('/')
        pkgcls = {'pypi': PyPiPkg, 'npm': NpmPkg}[prefix]
    except (ValueError, KeyError):
        print("Package names have to be prefixed with either pypi/ or npm/. Example: pypi/django")
        return
    try:
        mainpkg = pkgcls(pkgname)
    except HTTPError as e:
        print("Can't fetch {}. Does it even exist?".format(e.filename))
        return
    print("Getting dependencies...")
    try:
        deps = get_flat_deps(mainpkg, verbose=args.verbose)
    except HTTPError as e:
        print("Can't fetch {}. Could be a broken dependency.".format(e.filename))
        return
    allpkgs = {mainpkg} | deps
    print("Counting SLOC...")
    sloc_total = 0
    pkgcount = 0
    for pkg in allpkgs:
        try:
            sloc = pkg.get_tarball_sloc()
            sloc_total += sloc
            pkgcount += 1
            if args.verbose:
                print("{}: {:,}".format(pkg.name, sloc))
        except ValueError:
            print("WARNING: Can't download {}'s archive, so we can't count SLOC. Skipping")
    print("{:,} SLOC in {} packages needed to provide you with {}'s functionalities".format(
        sloc_total, pkgcount, mainpkg.name
    ))
    base_name, sloc = BASE_REQUIREMENTS[prefix]
    print("... not counting {} which is itself {} SLOC".format(base_name, sloc))
    print("NASA flies to **space** with 400k sloc")

if __name__ == '__main__':
    main()


