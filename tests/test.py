#!/usr/bin/env python

import os
import sys
import glob
import shutil
import argparse

from test.functions	import run_test
from test.mesmer	import tests as mesmer_tests
from test.utilities	import tests as utility_tests

"""
An automated testing script for the MESMER package.
"""

if(__name__ == "__main__"):
	parser = argparse.ArgumentParser(description='Provides automated testing of the MESMER CLI programs')

	parser.add_argument('test',		nargs='*',				default=[],		help='Specifies the test(s) to run')
	parser.add_argument('-all',		action='store_true',	default=False,	help='List all available tests')
	parser.add_argument('-clean',	action='store_true',	default=False,	help='Removes all output files')
	parser.add_argument('-path',							default=None,	help='Path to directory containing mesmer and utilities')
	parser.add_argument('-out',								default='.',	help='Path to save test output results')

	args	= parser.parse_args()

	if args.path == None:
		exe_dir = os.path.abspath( os.path.join(os.path.dirname(os.path.dirname(__file__)),"..",'mesmer') )
	else:
		exe_dir = os.path.abspath( args.path )

	data_dir = os.path.abspath( os.path.join(os.path.dirname(__file__),'data') )
	out_dir = os.path.abspath( os.path.join(args.out,'out') )

	def rm_out():
		try:
			shutil.rmtree( out_dir )
		except:
			pass

	if(args.clean):
		rm_out()
		sys.exit(0)

	tests = mesmer_tests()
	tests.extend( utility_tests() )

	if( len(args.test) == 0 and not args.all ):
		print "\nAvailable tests: "
		for (name,test) in tests:
			print "\t",
			print name
		print ""
		sys.exit(0)

	# prep the output directory
	rm_out()
	os.mkdir( out_dir )

	for (name,test) in tests:
		if args.all or name in args.test:
			run_test(name, test, (exe_dir,data_dir,out_dir), args )

	sys.exit(0)
