import unittest
import os
import sys

try:
	import mesmer
except ImportError:
	sys.path.append(os.path.abspath(".."))
	import mesmer

from base import *

if __name__ == '__main__':
	unittest.main()