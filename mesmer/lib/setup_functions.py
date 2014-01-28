import os
import sys
import shutil
import argparse
import shelve
import platform

from exceptions				import *
from utility_functions		import *

def parse_arguments(str=None):
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

	class mesParser(argparse.ArgumentParser):
		def error(self, message):
			self.print_usage()
			sys.exit(1)

	# argument groups are just used for more attractive formatting when help is invoked
	argparse.ArgumentParser.convert_arg_line_to_args = convert_arg_line_to_args
	parser = mesParser(fromfile_prefix_chars='@')

	group0 = parser.add_argument_group('Target and component files')
	group0.add_argument('-target',		action='append',	default=[],						metavar='FILE.target',			help='MESMER target file')
	group0.add_argument('-components',	action='append',	default=[],		nargs='*',		metavar='FILE.component/DIR',	help='MESMER component files or directory ')
	group0.add_argument('-resume',															metavar='STATE.tbl',			help='Resume from a provided ensemble state')

	group1 = parser.add_argument_group('Simulation size and convergence parameters')
	group1.add_argument('-name',		action='store',		default='MESMER_Results',		metavar='NAME',	help='Name of this run - a directory will be created with this name to contain all MESMER output')
	group1.add_argument('-dir',			action='store',		default='./',					metavar='DIR',	help='Directory in which to create results folder')
	group1.add_argument('-ensembles',	action='store',		default=1000,	type=int,		metavar='1000',	help='Number of ensembles to use in the algorithm')
	group1.add_argument('-size',		action='store',		default=3,		type=int,		metavar='3',	help='Number of components per ensemble')
	group1.add_argument('-Fmin',		action='store',		default=0.00,	type=float,		metavar='0.00',	help='Maximum ensemble fitness to stop algorithm')
	group1.add_argument('-Smin',		action='store',		default=0.00,	type=float,		metavar='0.01',	help='Minimum ensemble fitness stdev to stop algorithm')

	group2 = parser.add_argument_group('Genetic algorithm coefficients')
	group2.add_argument('-Gmax',		action='store',		default=-1,		type=int,		metavar='Inf',	help='Maximum number of generations, set to -1 to run indefinitely')
	group2.add_argument('-Gcross',		action='store',		default=0.8,	type=float,		metavar='0.8',	help='Ensemble component crossing frequency')
	group2.add_argument('-Gmutate',		action='store',		default=1.0,	type=float,		metavar='1.0',	help='Ensemble component mutation frequency')
	group2.add_argument('-Gsource',		action='store',		default=0.1,	type=float,		metavar='0.1',	help='Ensemble component mutation source frequency')

	group3 = parser.add_argument_group('Variable component ratio parameters')
	group3.add_argument('-Rforce'	,	action='store_true',default=False,									help='Force ensemble ratio reoptimization at every generation.')
	group3.add_argument('-Ralgorithm',	action='store',		default=3,	type=int,	choices=[0,1,2,3,4,5,6],	metavar='3',	help='Algorithm to use for optimal component ratios (0-6), 0=no ratio optimization')
	group3.add_argument('-Rprecision',	action='store',		default=0.01,	type=float,		metavar='0.01',	help='Precision of weighting algorithm')
	group3.add_argument('-Rn',			action='store',		default=-1,		type=int,		metavar='10N',	help='Number of weighting algorithm iterations')
	group3.add_argument('-boots',		action='store',		default=200,	type=int,		metavar='200',	help='The number of bootstrap samples for component weighting error analysis. 0=no error analysis')

	group4 = parser.add_argument_group('Output options')
	group4.add_argument('-Pstats',		action='store_true',default=True,									help='Print ensemble information at each generation. NOTE: always enabled')
	group4.add_argument('-Pbest',		action='store_true',default=True,									help='Print best ensemble information at each generation.')
	group4.add_argument('-Pstate',		action='store_true',default=True,									help='Print ensemble ratio state at each generation')
	group4.add_argument('-Popt',		action='store_true',default=False,									help='Print optimization convergence status for all ensembles.')
	group4.add_argument('-Pextra',		action='store_true',default=False,									help='Print extra restraint-specific information.')
	group4.add_argument('-Pmin',		action='store',		default=1.0,	type=float,		metavar='1.0',	help='Print conformer statistics only if they exist in this percentage of ensembles or greater.')
	group4.add_argument('-Pcorr',		action='store',		default=1.0,	type=float,		metavar='1.0',	help='Print conformer correlations only if they exist in this percentage of ensembles or greater.')

	group5 = parser.add_argument_group('Miscellaneous options')
	group5.add_argument('-seed',		action='store',		default=1,		type=int,		metavar='1',	help='Random number generator seed value to use.')
	group5.add_argument('-uniform',		action='store_true',default=False,									help='Load ensembles uniformly from available components instead of randomly')
	group5.add_argument('-force',		action='store_true',default=False,									help='Enable overwriting of previous output directories.')
	group5.add_argument('-threads',		action='store',		default=1,		type=int,		metavar='1',	help='Number of multiprocessing threads to use.')
	group5.add_argument('-scratch',		action='store',		default=None,					metavar='DIR',	help='Scratch directory in which to save temporary files.')
	group5.add_argument('-plugin',		action='store',										metavar='NAME',	help='Print information about the specified plugin and exit.')

	if(str == None):
		args = parser.parse_args()
	else:
		args = parser.parse_args(str.split())

	# argument error checking and defaults
	if (args.Rn < 0):
		args.Rn = args.size * 10

	# Windows runs afoul of multiprocessing atm
	if (platform.system() == 'Windows' and args.threads > 1):
		print_msg("WARNING: Multiprocessing not currently available on Windows, setting -threads to 1")
		args.threads = 1

	return args

def make_results_dir( args ):
	"""
	Creates a directory in which to save MESMER output files, and copies the parameters file into it
	"""

	args.dir = os.path.join( args.dir, args.name)

	oWrite = False
	if args.force and os.path.isdir(args.dir):
		oWrite = True
		try:
			shutil.rmtree(args.dir)
		except OSError:
			raise mesSetupError("ERROR: Could not delete directory \"%s\"." % (args.dir))

	if os.path.isdir(args.dir):
		raise mesSetupError("ERROR: MESMER results directory \"%s\" already exists." % (args.dir))

	# Prep the folders to recieve the results
	try:
		os.mkdir(args.dir)
	except OSError:
		raise mesSetupError("ERROR: Couldn't create MESMER results directory \"%s\"." % (args.dir))

	try:
		print_msg('',os.path.join(args.dir,"mesmer_log.txt"))
	except Exception as e:
		raise mesSetupError("ERROR: Couldn't open MESMER log file: %s" % e)

	try:
		db = shelve.open( os.path.join(args.dir,'mesmer_log.db') )
		db['args'] = args
		db.close()
	except:
		raise mesSetupError("ERROR: Couldn't open MESMER results database file")

	if(oWrite):
		print_msg("INFO: Overwriting old result directory \"%s\"" % (args.dir))