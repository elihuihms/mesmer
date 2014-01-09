#!/usr/bin/env python

import os
import sys
import glob
import shutil
import argparse

from test.functions	import run_test
from test.mesmer	import tests as mesmer_tests
from test.utilities	import tests as utility_tests

if(__name__ == "__main__"):
	parser = argparse.ArgumentParser()

	parser.add_argument('test',		nargs='*',					default=[] )	
	parser.add_argument('-all',		action='store_true',	default=False )
	parser.add_argument('-clean',	action='store_true',	default=False )

	path	= os.path.dirname(os.path.abspath(__file__))
	args	= parser.parse_args()

	def rm_out():
		try:
			shutil.rmtree( os.path.join(path,'out') )
		except:
			pass

	if(args.clean):
		rm_out()
		sys.exit(0)

	tests = mesmer_tests()
	tests.extend( utility_tests() )

	if( len(args.test) == 0 and not args.all ):
		print "Available tests: "
		for (name,test) in tests:
			print "\t",
			print name
		print ""
		sys.exit(0)

	# prep the output directory
	rm_out()
	os.mkdir( os.path.join(path,'out') )
	
	for (name,test) in tests:
		if args.all or name in args.test:
			run_test(name, test, path, args )
			
	sys.exit(0)
