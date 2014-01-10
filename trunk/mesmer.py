#!/usr/bin/env python

import sys
import os

from lib import __version__
from lib.exceptions				import *
from lib.setup_functions		import parse_arguments,make_results_dir
from lib.utility_functions		import print_msg
from lib.plugin_functions		import load_plugins,unload_plugins
from lib.target_functions		import load_targets
from lib.component_functions	import load_components
from lib.ga_functions_main		import run_ga

def run():
	if( sys.version_info < (2,5) ):
		print "Python version must be 2.5 or greater"
		sys.exit()

	# obtain the parameters for the run
	args = parse_arguments()

	# attempt to load available plugin modules
	try:
		plugins = load_plugins(os.path.dirname(__file__), 'mesmer', args )
	except mesPluginError as e:
		print e.msg
		sys.exit(10)

	# did the user request information about a plugin?
	for p in plugins:
		if (args.plugin == p.name) or (args.plugin in p.type):
			p.info()
			sys.exit(0)

	if len(plugins) == 0:
		raise mesPluginError("ERROR: No valid plugins found in %s." % (os.path.dirname(__file__)) )

	# attempt to create the fitting results directory
	try:
		make_results_dir(args)
	except mesSetupError as e:
		print e.msg
		sys.exit(20)

	# save the parameters list to the log file
	print_msg("MESMER v. %s \n(c)2012-2014 Elihu Ihms" % (__version__))
	print_msg("Arguments:")
	for k in vars(args):
		print_msg("\t%s\t:\t%s" % (k,vars(args)[k]))
	print_msg("")

	# load target restraints by passing off to plugins
	try:
		targets = load_targets( args, plugins )
	except mesTargetError as e:
		print e.msg
		sys.exit(30)

	# create component database
	try:
		components = load_components( args, plugins, targets )
	except mesComponentError as e:
		print e.msg
		sys.exit(40)

	# Start the algorithm
	ret = run_ga( args, plugins, targets, components )

	# finished, unload plugins
	try:
		unload_plugins( plugins )
	except mesPluginError as e:
		print e.msg
		sys.exit(41)

if( __name__ == "__main__" ):
	try:
		run()
	except KeyboardInterrupt:
		print_msg( "\nINFO: User forced quit, exiting.\n" )
		sys.exit(0)
