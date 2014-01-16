import sys

from datetime				import datetime

from exceptions				import *
from ga_functions_mp		import *
from ga_functions_misc		import *
from ga_functions_stats		import *
from ga_functions_output	import *

def run_ga( args, plugins, targets, components ):
	"""
	Evolves a set of ensembles until a combination of components is found that best fits the provided target dataset

	Returns nothing, as all output is handled by other functions or plugin methods

	Arguments:
	args		- The MESMER parameters argument object
	plugins		- A list of plugin modules to interpret and evaluate the various types of target and component attributes
	targets		- A list of targets containing the data to be fit
	components	- A list of possible components to be used in recreating/fitting the target data
	"""

	print_msg("\nAlgorithm starting on %s." % datetime.utcnow() )

	print "\tCreating parent ensembles..."
	sys.stdout.flush()

	parents = make_ensembles( args, plugins, targets, components )

	print "\tOptimizing parent component ratios..."
	sys.stdout.flush()

	parents = mp_optimize_ratios( args, components, plugins, targets, parents )

	generation_counter = 0
	loop = True
	while( loop ):
		print_msg( "\nGeneration %i" % (generation_counter) )
		sys.stdout.flush()

		# create clones of the parents, and subject to genetic modification
		offspring = copy.deepcopy(parents)

		print "\tEvolving offspring..."
		sys.stdout.flush()

		evolve_ensembles( args, components, offspring )

		print "\tOptimizing offspring component ratios..."
		sys.stdout.flush()

		# optimize component ratios for newly-mutated/crossed offspring
		offspring = mp_optimize_ratios( args, components, plugins, targets, offspring )

		# retrieve the 1/2 best-scoring ensembles and some collected statistics
		(best_scored,ensemble_stats) = get_best_ensembles( args, targets, parents, offspring )

		# get the relative fitness contribution for each restraint type
		restraint_stats = get_restraint_stats( args, targets, best_scored )

		# print the status and selected statistics
		print_generation_state( args, generation_counter, ensemble_stats, restraint_stats )

		if(args.Pstats):
			# print component correlations from the current ensembles
			write_component_stats( args, generation_counter, best_scored )

			# print collected information on the current ensembles
			write_ensemble_stats( args, generation_counter, targets, best_scored )

		if(args.Pstate):
			# save the current ensemble population ratios
			write_ensemble_state( args, generation_counter, targets, best_scored )

		if(args.Popt):
			# write the ratio optimization state for the current ensembles
			write_optimization_state( args, generation_counter, targets, best_scored )

		if(args.Pbest):
			# print information about the best-scoring ensemble

			if(args.boots > 0):
				print "\tCalculating best fit statistics..."
				sys.stdout.flush()

			# get the error intervals for the best ensemble component ratios
			best_ratio_errors = get_ratio_errors( args, components, plugins, targets, [best_scored[0]] )
			print_ensemble_state( args, best_ratio_errors[0] )

		if(args.Pextra):
			# call the various output methods of the plugins
			print_plugin_state( args, generation_counter, plugins, targets, best_scored )

		# loop exit criteron
		if( ensemble_stats['scores'][args.size] < args.Fmin ):
			print_msg(  "\nMaximum ensemble score is less than Fmin, exiting." )
			loop = False

		if( (ensemble_stats['total'][2]/ensemble_stats['total'][1]) < args.Smin ):
			print_msg(  "\nEnsemble score RSD is less than Smin, exiting." )
			loop = False

		if (args.Gmax > -1) and (generation_counter >= args.Gmax):
			print_msg(  "\nGeneration counter has reached Gmax, exiting." )
			loop = False

		# set up for the next generation
		parents = best_scored
		generation_counter += 1

	sys.stdout.flush()

	return
