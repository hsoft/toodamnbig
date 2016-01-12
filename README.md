# That dependency is too damn big!

**Tell that ninja dev to get off your lawn!**

![Too Damn Big!](https://raw.github.com/hsoft/toodamnbig/master/images/toodamnbig.jpg)

This is a small script that takes a NPM package name and tells how heavy that package is, including
its dependencies. That gives you ammunition to keep people who are trigger-happy with dependencies
at bay.

## Requirements

* Python 3.4+

## Usage

Clone the repo and execute the script directly:

    $ python3 toodamnbig.py browserify
    Getting dependencies...
    89,413 SLOC in 116 packages needed to provide you with browserify's functionalities
    ... not counting Node which is itself 5M SLOC
    NASA flies to **space** with 400k sloc

## Roadmap

* PyPI support
* RubyGems support
* Version stability stats (warning about very frequent releases)
* Detailed output
* `package.json`, `setup.py`, `requirements.txt`, `Gemfile` parsing

## License

GPLv3

