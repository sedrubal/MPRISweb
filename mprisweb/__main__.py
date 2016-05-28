#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

"""
The main entry point.
"""

from __future__ import absolute_import
from __future__ import print_function

import sys
from mprisweb.mprisweb import main

print("[!] ATTENTION:")
print("[!] ==========")
print("[!]    running script which is installed by setup.py")
print("[!]    will not completely work but behave strange.")
print("[!]    I don't know what's the problem...")
sys.exit(main())
