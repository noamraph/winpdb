#! /usr/bin/env python

"""
    Functional tests for rpdb2

    Copyright (C) 2013-2017 Philippe Fremy

    This program is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation; either version 2 of the License, or any later
    version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02111-1307 USA
"""
import unittest, sys

from tests.test_rpdb2 import *

if __name__ == '__main__':
    unittest.main( argv=[sys.argv[0] + '-v'] + sys.argv[1:] )
