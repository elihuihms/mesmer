import os
import sys
import shutil
import argparse
import shelve
import platform

from exceptions				import *
from utility_functions		import *

def parse_arguments(args=None,prefs=None):
	"""Parses the command-line parameters (or those provided in a configuration file)"""

	class mesParser(argparse.ArgumentParser):
		def error(self, message):
			print "ERROR:\tArgument parser encountered an error: %s"%(message)
#			self.print_usage()
			sys.exit(1)

		# default behavior of argparse is to split on newlines in argument list files
		# this allows for both the argument and value to be on the same line
		def convert_arg_line_to_args(self, line):
			line = line.strip()
			if not line:
				return []
			if line[0] == '#':
				return []
			return line.split(' ',1)

	# argument groups are just used for more attractive formatting when help is invoked
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
	group3.add_argument('-Ralgorithm',	action='store',		default=3,	type=int,	choices=[0,1,2,3,4,5,6],	metavar='6',	help='Algorithm to use for optimal component ratios (0-6), 0=no ratio optimization. Consult the mesmer docs for more information.')
	group3.add_argument('-Rprecision',	action='store',		default=0.01,	type=float,		metavar='0.01',	help='Precision of weighting algorithm')
	group3.add_argument('-Rn',			action='store',		default=-1,		type=int,		metavar='10*size',	help='Number of weighting algorithm iterations. Defaults to ensemble size x10')
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
	group5.add_argument('-seed',		action='store',		default=1,		type=int,		metavar='N',	help='Random number generator seed value to use.')
	group5.add_argument('-uniform',		action='store_true',default=False,									help='Load ensembles uniformly from available components instead of randomly')
	group5.add_argument('-force',		action='store_true',default=False,									help='Enable overwriting of previous output directories.')
	group5.add_argument('-threads',		action='store',		default=1,		type=int,		metavar='N',	help='Number of multiprocessing threads to use.')
	group5.add_argument('-scratch',		action='store',		default=None,					metavar='DIR',	help='Scratch directory in which to save temporary files.')
	group5.add_argument('-plugin',		action='store',										metavar='NAME',	help='Print information about the specified plugin and exit.')
	group5.add_argument('-reset',		action='store_true',default=False,									help='Reset saved MESMER preferences.')

	if args != None:	
		ret = parser.parse_args(args)
	else:
		ret = parser.parse_args() # get from sys.argv

	# set run arguments from preferences
	if prefs != None:
		for action in [a.__dict__ for a in parser.__dict__['_actions']]:
			name,value,default = action['dest'],getattr(ret,action['dest'],None),action['default']
			if value == None:
				continue
			if value == default and name in prefs['run_arguments']:
				print "INFO:\tOverwriting argument \"-%s\" default to \"%s\" based on user preferences."%(name,prefs['run_arguments'][name])
				setattr(ret, name, prefs['run_arguments'][name])
				
	# argument error checking and defaults
	if (ret.Rn < 0):
		ret.Rn = ret.size * 10

	return ret

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
			raise mesSetupError("ERROR:\tCould not delete directory \"%s\"." % (args.dir))

	if os.path.isdir(args.dir):
		raise mesSetupError("ERROR:\tMESMER results directory \"%s\" already exists." % (args.dir))

	# Prep the folders to recieve the results
	try:
		os.mkdir(args.dir)
	except OSError:
		raise mesSetupError("ERROR:\tCouldn't create MESMER results directory \"%s\"." % (args.dir))

	try:
		print_msg('',os.path.join(args.dir,"mesmer_log.txt"))
	except Exception as e:
		raise mesSetupError("ERROR:\tCouldn't open MESMER log file: %s" % e)

	try:
		db = shelve.open( os.path.join(args.dir,'mesmer_log.db') )
		db['args'] = args
		db.close()
	except:
		raise mesSetupError("ERROR:\tCouldn't open MESMER results database file.")

	if(oWrite):
		print_msg("INFO:\tOverwriting old result directory \"%s\"." % (args.dir))
		
def open_user_prefs( mode='r' ):
	from . import __version__ as base_version
	from gui import __version__ as gui_version
	import anydbm
	
	home = os.path.expanduser("~")
	path = os.path.join( home, ".mesmer_prefs" )
	try:
		shelf = shelve.open( path, mode )
	except anydbm.error as e:
		raise mesSetupError(str(e))
	
	def update_prefs( shelf ):
		set_default_prefs( shelf )		
		shelf.sync()
	
	if 'base-version' not in shelf or 'gui-version' not in shelf:
		print_msg("INFO:\tCreating MESMER preferences file at \"%s\"."%path)
		set_default_prefs( shelf )
	
	# don't use prefs from old installation
	def vsplit(v):
		return tuple(map(int,(v.split('.'))))
	
	if vsplit(shelf['base-version']) < vsplit(base_version):
		print_msg("INFO:\tUpdating MESMER preferences file."%path)
		set_default_prefs( shelf )
		
	if vsplit(shelf['gui-version']) < vsplit(gui_version):
		print_msg("INFO:\tUpdating MESMER preferences file."%path)
		set_default_prefs( shelf )
	
	return shelf
	
def set_default_prefs( shelf ):
	from . import __version__ as base_version
	from gui import __version__ as gui_version
	from multiprocessing import cpu_count
	
	shelf['base-version'] = base_version
	shelf['gui-version'] = gui_version
	shelf['mesmer_base_dir'] = ''
	shelf['mesmer_scratch'] = ''
	shelf['cpu_count'] = cpu_count()
	shelf['run_arguments'] = {'threads':shelf['cpu_count']}
	shelf['disabled_plugins'] = []
	shelf['plugin_prefs'] = {}
	shelf.sync()