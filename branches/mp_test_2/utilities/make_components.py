#!/usr/bin/env python

import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.component_generation	import *
from lib.exceptions				import *

def run():
	parser = argparse.ArgumentParser(usage='make_conformers [options]')

	parser.add_argument('-template',	action='store',		required=True,			metavar='FILE',		help='Component template file')
	parser.add_argument('-values',		action='store',		required=True,			metavar='FILE',		help='Component values table file')
	parser.add_argument('-data',		action='store',		default=[],	nargs='*',	metavar='DIR(s)',	help='Component data file directory')
	parser.add_argument('-out',			action='store',		default='components',	metavar='DIR',		help='Output directory name')
	args = parser.parse_args()

	if os.path.isdir(args.out):
		print "ERROR: component output directory \"%s\" already exists." % (args.out)
		sys.exit(1)

	try:
		os.mkdir(args.out)
	except OSError:
		print "ERROR: Couldn't create component output directory \"%s\"." % (args.out)
		sys.exit(2)

	try:
		handle = open( args.template, 'r' )
	except IOError:
		print "ERROR: Could not open template file %s " % (args.template)
		sys.exit(3)

	template = handle.read()
	handle.close()

	try:
		component_vals = get_component_values( args.values )
	except ComponentGenException as e:
		print e.msg
		sys.exit(4)

	try:
		component_dirs = match_data_files( component_vals.keys(), args.data )
	except ComponentGenException as e:
		print e.msg
		sys.exit(5)

	try:
		write_component_files( component_vals, component_dirs, template, args.out )
	except  ComponentGenException as e:
		print e.msg
		sys.exit(6)

	sys.exit(0)

if( __name__ == "__main__" ):
	run()