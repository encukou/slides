#! /usr/bin/python

import sys
import os
import glob
import doctest

os.chdir('samples')
sys.path.insert(0, os.path.abspath('.'))

failed = 0

for filename in glob.glob("*.txt"):
    result = doctest.testfile(filename, optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    failed += result.failed

exit(failed)
