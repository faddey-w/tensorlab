#! /usr/bin/env python

import sys
import unittest


if len(sys.argv) == 1:
    sys.argv.extend(['discover', '-s', 'test_tensorlab'])
else:
    sys.argv.insert(1, 'discover')

unittest.main(module=None)
