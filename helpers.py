"""
CLI helperfunctions
"""

from __future__ import print_function
import sys

VERBOSITY = 0


def set_verbosity(value):
    """Sets the verbosity to value"""
    # TODO this is dirty...
    global VERBOSITY
    VERBOSITY = value


def log(msg, min_verbosity=0, error=False):
    """log to stdout, if verbosity >= min_verbosity"""
    if VERBOSITY >= min_verbosity:
        print(
            ('[!] {0}' if error else '[i] {0}').format(msg),
            file=sys.stderr if error else sys.stdout
        )
