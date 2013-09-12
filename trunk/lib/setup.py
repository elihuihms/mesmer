import os
import os.path
import sys
import shutil
import re
import glob
import argparse
import shelve
import tempfile

from lib.ga_objects_target import mesTarget
from lib.ga_objects_component import mesComponent
from lib.functions import print_msg

"""
Functions for setting up a MESMER run
"""

def parse_param_arguments(str=None):
	"""
	Parses the command-line parameters (or those provided in a configuration file)
	"""

	# default behavior of argparse is to split on newlines in  argument list files
	# this allows for both the argument and value to be on the same line
	def convert_arg_line_to_args(self, arg_line):
		for arg in arg_line.split():
			if not arg.strip():
				continue
			yield arg

	# argument groups are just used for more attractive formatting when help is invoked
	argparse.ArgumentParser.convert_arg_line_to_args = convert_arg_line_to_args
	parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

	group0 = parser.add_argument_group('Target and component files')
	group0.add_argument('-target',		action='append',									metavar='FILE.target',			help='MESMER target file')
	group0.add_argument('-components',	action='append',	nargs='*',						metavar='FILE.component/DIR',	help='MESMER component files or directory ')
	group0.add_argument('-resume',															metavar='STATE.tbl',			help='Resume from a provided ensemble state')

	group1 = parser.add_argument_group('Simulation size and convergence parameters')
	group1.add_argument('-name',		action='store',		default='MESMER_Results',		metavar='NAME',	help='Name of this run - a directory will be created with this name to contain all MESMER output')
	group1.add_argument('-dir',			action='store',		default='./',					metavar='DIR',	help='Directory in which to create results folder')
	group1.add_argument('-ensembles',	action='store',		default=1000,	type=int,		metavar='N',	help='Number of ensembles to use in the algorithm')
	group1.add_argument('-size',		action='store',		default=3,		type=int,		metavar='N',	help='Number of components per ensemble')
	group1.add_argument('-Fmin',		action='store',		default=-1,		type=float,		metavar='F',	help='Maximum ensemble fitness to stop algorithm')
	group1.add_argument('-Smin',		action='store',		default=0,		type=float,		metavar='F',	help='Minimum ensemble fitness stdev to stop algorithm')

	group2 = parser.add_argument_group('Genetic algorithm coefficients')
	group2.add_argument('-Gmax',		action='store',		default=-1,		type=int,		metavar='N',	help='Maximum number of generations, set to -1 to run indefinitely')
	group2.add_argument('-Gcross',		action='store',		default=0.8,	type=float,		metavar='F',	help='Ensemble component crossing frequency')
	group2.add_argument('-Gmutate',		action='store',		default=1.0,	type=float,		metavar='F',	help='Ensemble component mutation frequency')
	group2.add_argument('-Gsource',		action='store',		default=0.1,	type=float,		metavar='F',	help='Ensemble component mutation source frequency')

	group3 = parser.add_argument_group('Variable component ratio parameters')
	group3.add_argument('-Rforce'	,	action='store_true',default=False,									help='Force ensemble ratio reoptimization at every generation.')
	group3.add_argument('-Ralgorithm',	action='store',		default=3,	type=int,	choices=[0,1,2,3,4,5,6],	metavar='N',	help='Algorithm to use for optimal component ratios (0-6), 0=no ratio optimization')
	group3.add_argument('-Rprecision',	action='store',		default=0.01,	type=float,		metavar='F',	help='Precision of weighting algorithm')
	group3.add_argument('-Rn',			action='store',		default=-1,		type=int,		metavar='N',	help='Number of weighting algorithm iterations')
	group3.add_argument('-boots',		action='store',		default=200,	type=int,		metavar='N',	help='The number of bootstrap samples for component weighting error analysis. 0=no error analysis')

	group4 = parser.add_argument_group('Output options')
	group4.add_argument('-Pstats',		action='store_true',default=True,									help='Print ensemble information at each generation. NOTE: always enabled')
	group4.add_argument('-Pbest',		action='store_true',default=True,									help='Print best ensemble information at each generation.')
	group4.add_argument('-Popt',		action='store_true',default=False,									help='Print optimization convergence status for all ensembles.')
	group4.add_argument('-Pextra',		action='store_true',default=False,									help='Print extra restraint-specific information.')
	group4.add_argument('-Pstate',		action='store_true',default=False,									help='Print ensemble ratio state at each generation')
	group4.add_argument('-Pmin',		action='store',		default=1.0,	type=float,		metavar='F',	help='Print conformer statistics only if they exist in this percentage of ensembles or greater.')
	group4.add_argument('-Pcorr',		action='store',		default=1.0,	type=float,		metavar='F',	help='Print conformer correlations only if they exist in this percentage of ensembles or greater.')

	group5 = parser.add_argument_group('Miscellaneous options')
	group5.add_argument('-seed',		action='store',		default=1,		type=int,		metavar='N',	help='Random number generator seed value to use.')
	group5.add_argument('-uniform',		action='store_true',default=False,									help='Load ensembles uniformly from available components instead of randomly')
	group5.add_argument('-force',		action='store_true',default=False,									help='Enable overwriting of previous output directories.')
	group5.add_argument('-threads',		action='store',		default=1,		type=int,		metavar='N',	help='Number of multiprocessing threads to use.')
	group5.add_argument('-dbm',			action='store_true',default=False,									help='Use a component database instead of maintaining in memory (much slower, significantly reduced memory footprint')
	group5.add_argument('-plugin',		action='store',										metavar='NAME',	help='Print information about the specified plugin and exit.')

	if(str == None):
		args = parser.parse_args()
	else:
		args = parser.parse_args(str.split())

	# argument error checking and defaults
	if (args.Rn < 0):
		args.Rn = args.size * 10

	return args

def make_results_dir( args ):
	"""
	Creates a directory in which to save MESMER output files, and copies the parameters file into it
	"""

	path = os.path.abspath( "%s%s%s" % (args.dir,os.sep,args.name) )
	args.dir = path

	if args.force and os.path.isdir(path):
		print_msg("INFO: Overwriting old result directory \"%s\"" % (path))

		try:
			shutil.rmtree(path)
		except OSError:
			print "ERROR: Could not delete directory \"%s\"." % (path)
			return False

	if os.path.isdir(path):
		print "ERROR: MESMER results directory \"%s\" already exists." % (path)
		return False

	# Prep the folders to recieve the results
	try:
		os.mkdir(path)
	except OSError:
		print "ERROR: Couldn't create MESMER results directory \"%s\"." % (path)
		return False

	return True

def load_all_targets( args, plugins ):
	"""
	Loads all targets specified in the args by passing them off to the appropriate plugins
	"""

	if(len(args.target) < 0):
		return [None]

	names, targets = [], []

	for f in args.target:
		print_msg("INFO: Reading target file \"%s\"" % (f))

		targets.append( mesTarget() )

		if( not targets[-1].load(f,plugins) ):
			print_msg("ERROR: Could not load target file \"%s\"." % (f))
			targets[-1] = None
			return targets

		if( targets[-1].name in names ):
			print_msg("ERROR: Target file \"%s\" has the same name (%s) as a previous target." % (f,targets[-1].name))
			targets[-1] = None
			return targets

		names.append(targets[-1].name)

	return targets

def load_all_components( args, plugins, targets ):

	files = []
	for f in args.components:

		if( os.path.isdir(f[0]) ):
			files.extend( glob.glob( "%s%s*" % (f[0],os.sep) ) )
		else:
			files.extend( f )

	if(len(files) < 0):
		return [None]

	if( args.dbm ):
		print_msg("INFO: Loading %i component files to temporary database:" % (len(files)))

		path = "%s%scomponents.db" % (tempfile.mkdtemp(),os.sep)
		try:
			components = shelve.open( path )
		except:
			print_msg("ERROR: Could not create component database file \"%s\"." % (path) )
			return [None]
	else:
		print_msg("INFO: Found %i component files." % (len(files)))
		components = {}

	names = [''] * len(files)
	divisor = int(max(len(files)/100,1))
	for (i,f) in enumerate(files):
		if( i % divisor == 0 ):
			sys.stdout.write("\rComponent loading progress: %i%%" % (100.*i/len(files)+1) )
			sys.stdout.flush()

		temp = mesComponent()

		if( not temp.load(f,plugins,targets) ):
			print_msg("\nERROR: Could not load component file \"%s\"." % (f))
			return [None]

		if( temp.name in names ):
			print_msg("\nERROR: Component file \"%s\" has the same NAME as a previous component." % (f))
			return [None]

		# add the component to the component database
		components[temp.name] = temp
		names[i] = temp.name

	sys.stdout.write("\n")

	if( args.dbm ):
		components.close()

		# reopen components db as read-only
		components = shelve.open( path, flag='r' )

	return components
