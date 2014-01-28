#!/usr/bin/env python

import argparse
import os
import scipy
import sys
import glob

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.plugin_functions		import load_plugins, unload_plugins
from lib.target_functions		import load_targets
from lib.component_functions	import load_components
from lib.ensemble_objects		import mesEnsemble
from lib.ga_functions_output	import print_plugin_state

def run():
	parser = argparse.ArgumentParser()
	parser.add_argument('-target',		action='append',	required=True,					metavar='FILE',		help='Target file to use as template')
	parser.add_argument('-components',	action='append',	required=True,	nargs='*',		metavar='FILE/DIR',	help='MESMER component files or directory ')
	parser.add_argument('-spec',							required=True,					metavar='SPEC',		help='The synthetic target specification file')
	parser.add_argument('-dir',								default='./',					metavar='./',		help='Directory to write synthetic data to')
	parser.add_argument('-scratch',							default=None)

	args = parser.parse_args()
	args.dbm = False
	args.plugin = ''

	# god help you if there's errors here - no checking!
	plugins = load_plugins(	os.path.dirname(os.path.dirname(__file__)), 'mesmer', args )
	targets = load_targets( args, plugins )
	components = load_components( args, plugins, targets )

	if(None in components):
		exit()

	tmp = scipy.recfromtxt( args.spec, dtype=str, unpack=True )
	n = len(tmp[0])
	spec = [ list(tmp[0]), list(tmp[1]) ]

	# make sure all the specified components are available, and get their weighting
	for i in range(n):
		if( not spec[0][i] in components.keys() ):
			print "The specification component %s was not found in the provided components" % spec[0][i]
			exit()
		spec[1][i] = float(spec[1][i])

	e = mesEnsemble( plugins, targets, n )
	e.component_names = spec[0]
	o = e.get_fitness(components, plugins, targets[0], spec[1])

	print "Fits to provided target data:"
	for k in o:
		print "\t%s : %.3f" % (k,o[k])

	print_plugin_state( args, 0, plugins, targets, [e])
	unload_plugins( plugins )

if( __name__ == "__main__" ):
	run()