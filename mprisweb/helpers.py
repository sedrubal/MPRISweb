"""
CLI helperfunctions
"""

from __future__ import print_function

import __init__
import sys
import ipaddress
import argparse
try:
    import argcomplete
except ImportError:
    pass

VERBOSITY = 0


def ip_addr(value):
    """parse an ip address / checks if the given string is a valid ip"""
    try:
        return str(ipaddress.ip_address(unicode(value)))
    except ipaddress.AddressValueError as err:
        raise argparse.ArgumentError(err.message)


def parse_args(argv=sys.argv[1:]):
    """
    parse cmd line args and
    :return an object containing the args and their values (see argparse doc)
    """
    parser = argparse.ArgumentParser(description=__init__.__doc__)
    parser.add_argument(
        '-v',
        dest='verbosity',
        action='count',
        default=0,
        help="enable verbose log output",
    )
    parser.add_argument(
        '-p',
        dest='port',
        type=int,
        action='store',
        default=8888,
        help="the port to listen on (default: 8888)",
    )
    parser.add_argument(
        '-i',
        dest='ip',
        type=ip_addr,
        action='store',
        default=ip_addr("0.0.0.0"),
        help="the IP address to listen on (default: 0.0.0.0)",
    )

    if 'argcomplete' in globals():
        argcomplete.autocomplete(parser)

    args = parser.parse_args(argv)
    set_verbosity(args.verbosity)
    return args


def set_verbosity(value):
    """Sets the verbosity to value"""
    # this is dirty...
    global VERBOSITY
    VERBOSITY = value


def log(msg, min_verbosity=0, error=False):
    """log to stdout, if verbosity >= min_verbosity"""
    if VERBOSITY >= min_verbosity:
        print(
            ('[!] {0}' if error else '[i] {0}').format(msg),
            file=sys.stderr if error else sys.stdout
        )
