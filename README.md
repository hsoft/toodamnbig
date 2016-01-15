# That dependency is too damn big!

**Tell that ninja dev to get off your lawn!**

![Too Damn Big!](https://raw.github.com/hsoft/toodamnbig/master/images/toodamnbig.jpg)

This is a small script that takes a NPM or PyPI package name and tells how heavy that package is,
including its dependencies. That gives you ammunition to keep people who are trigger-happy with
dependencies at bay.

## Requirements

* Python 3.4+

## Usage

Clone the repo and execute the script directly:

    $ python3 toodamnbig.py npm/browserify
    Getting dependencies...
    89,413 SLOC in 116 packages needed to provide you with browserify's functionalities
    ... not counting Node which is itself 5M SLOC
    NASA flies to **space** with 400k sloc

## Arguments

There's one positional argument: the package name. It has to be prefixed by its type, `npm` or
`pypi`. For example, `npm/async` means the `async` package on NPM and `pypi/django` means the
Django package on PyPI.

Otherwise, there's the `--verbose` flag to make the output... more verbose!

## PyPI limitations

Extracting dependencies from a Python package is not always an easy thing. Packaging in Python went
through many phases, most of which requiring dependencies to be declared in `setup.py`, an
*executable* file. Yes, it means that to know the dependencies of such a package, you need to
execute a possibly untrusted script you've just downloaded from the internet.

Because I don't want to take the responsibility for possibly endangering your machine, I don't do
that. Instead, I tokenize the `setup.py` and extract dependencies from there. However, it only
works for "simple" dependencies declaration. As soon as you add dynamicity into the mix, it doesn't
work anymore.

Fortunately, there's the new "wheel" format available with many packages on PyPI. With this package
format, it's much easier to extract dependencies without running any arbitrary script. So, whenever
it can, this script will use the "wheel" format.

If, for any reason, dependencies can't be extracted for a package, there will be a warning in the
output.

## Roadmap

* RubyGems support
* Version stability stats (warning about very frequent releases)
* `package.json`, `setup.py`, `requirements.txt`, `Gemfile` parsing

## License

GPLv3

