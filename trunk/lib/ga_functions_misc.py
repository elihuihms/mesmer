import os
import os.path
import sys
import random
import math

from scipy					import optimize
from multiprocessing		import Process,Queue

from exceptions				import *
from ensemble_objects		import mesEnsemble
from utility_functions		import print_msg,mean_stdv
from optimization_functions	import blind_random_min,localized_random_min

def make_ensembles( args, plugins, targets, components ):
	"""
	Creates an initial set of ensembles using randomly selected components

	Returns a list of mesEnsembles

	Arguments:
	args		- The MESMER argument parameters
	targets		- A dict of mesTargets
	components	- The component to be randomly incorporated into the ensembles
	"""

	component_names = components.keys()

	ensembles = []
	for i in range( args.ensembles ):

		ensembles.append( mesEnsemble( plugins, targets, args.size ) )

		# randomly fill the new ensemble with components
		if(not args.uniform):
			ensembles[-1].fill( component_names )
		else:
			ensembles[-1].fill_uniform( i, component_names )

	# if we're resuming from a previous run, fill the ensembles with the specified makeup
	if( args.resume ):
		set_ensemble_state( args, ensembles, components )

	return ensembles

def evolve_ensembles( args, components, ensembles ):
	"""
	Applies genetic transformations to the provided ensembles.
	These consist of:
	1. Crossing, where the components (genes) of two ensembles are swapped
	2. Mutation, where a component of an ensemble is switched with another component

	Arguments:
	args		- The MESMER argument parameters
	components	- A list of all components available for mutation
	ensembles	- The ensembles to be worked upon
	"""

	# go through each evolution type separately
	for e in ensembles:

		# gene exchange (sexual) w/ random ensemble
		if(random.random() < args.Gcross):
			e.cross( random.choice(ensembles) )

	component_names = components.keys()

	for e in ensembles:

		# random mutation, either to any component, or a component present in the existing ensemble population
		e.mutate( component_names, ensembles, args.Gmutate, args.Gsource )

	return

def optimize_ratios( args, components, plugins, targets, ensembles, q, print_status=True ):
	"""
	Optimizes the component ratios of the provided ensembles.
	The actual algorithm used to achieve optimization is dependent upon the Ralgorithm element of the provided MESMER parameters dict
	This function returns nothing, as the modified ensembles are placed into a multiprocessing queue

	Arguments:
	args		- The MESMER argument parameters
	components	- The component database
	plugins		- A list of the data processing and evaluation plugin modules
	targets		- A list of mesTargets used to score the ensembles
	ensembles	- The ensembles to be worked upon
	q			- A multiprocessing.Queue object that the modified ensembles will be placed into
	"""

	# set up a bounding array for bounded optimizers
	ratio_bounds = [(0.0,None)] * args.size

	# delta function for fitness algorithm to pass to minimization function
	def wrapper( ratios ):
		return sum(e.get_fitness( components, plugins, t, ratios ).itervalues())

	n2 = len(targets)
	n1 = len(ensembles)
	divisor = int(max(n1/100,1))
	for t in targets:
		for (i,e) in enumerate(ensembles):

			if(i % divisor == 0) and (print_status):
				sys.stdout.write("\r\tComponent ratio optimization progress: %i%%\n" % (100.*i/(n1*n2)+1) )
				sys.stdout.flush()

			if(e.optimized[t.name]):
				continue
			elif( args.Ralgorithm == 0 ):
				e.get_fitness( components, plugins, t, [1.0/args.size] * args.size )
				e.opt_status[t.name] = 'N/A'

			elif( args.Ralgorithm == 1 ):
				e.ratios[t.name] = blind_random_min( wrapper, e.ratios[t.name], args.Rprecision, args.Rn )
				e.opt_status[t.name] = 'N/A'

			elif( args.Ralgorithm == 2 ):
				e.ratios[t.name] = localized_random_min( wrapper, e.ratios[t.name], args.Rprecision, args.Rn )
				e.opt_status[t.name] = 'N/A'

			elif( args.Ralgorithm == 3 ):
				(e.ratios[t.name],nfeval,status) = optimize.fmin_tnc( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=args.Rn, messages=0, accuracy=args.Rprecision )
				e.opt_status[t.name] = optimize.tnc.RCSTRINGS[status]

			elif( args.Ralgorithm == 4 ):
				(e.ratios[t.name],fopt,status) = optimize.fmin_l_bfgs_b( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=args.Rn, disp=False, epsilon=args.Rprecision)
				e.opt_status[t.name] = status['warnflag']

			elif( args.Ralgorithm == 5 ):
				(e.ratios[t.name],fopt,direc,iter,funcalls,e.opt_status[t.name]) = optimize.fmin_powell(wrapper, e.ratios[t.name], disp=0, full_output=True, maxfun=args.Rn, xtol=args.Rprecision)

			elif( args.Ralgorithm == 6 ):
				(e.ratios[t.name],fopt,iter,funcalls,e.opt_status[t.name]) = optimize.fmin( wrapper, e.ratios[t.name], xtol=args.Rprecision, maxfun=args.Rn, full_output=True, disp=False)

			# set optimization flag!
			if( (e.opt_status[t.name] != 0) or args.Rforce ):
				e.optimized[t.name] = False
			else:
				e.optimized[t.name] = True

			# normalize ensemble ratios for the target
			e.normalize(t.name)

	q.put(ensembles)
	return

def mp_optimize_ratios( args, components, plugins, targets, ensembles, print_status=True ):
	"""
	A multiprocessing wrapper for the function optimize_ratios.
	See that function's docstrings for more information.

	Returns a copy of the provided ensembles that have had their component ratios optimized
	"""

	q = Queue()
	chunksize = int(math.ceil(len(ensembles) / float(args.threads)))

	# randomize ensemble order so threads should finish processing their chunks in about the same time
	random.shuffle( ensembles )

	procs = []
	for i in range( args.threads ):
		p = Process(target=optimize_ratios, args=(args,components,plugins,targets,ensembles[ chunksize * i : chunksize * (i +1) ],q,print_status))
		procs.append( p )
		p.start()

	ensembles = []
	for i in range( args.threads ):
		ensembles.extend( q.get() )

	for p in procs:
		p.join()

	return ensembles

def calculate_fitnesses( targets, ensembles ):
	"""
	Sum the fitness scores of every ensemble for each target

	Returns a target-name-keyed dict of scores for each ensemble

	Arguments:
	targets		- A list of mesTarget targets used to score the ensembles
	ensembles	- A list of mesEnsemble ensemble objects to be scored
	"""
	scores = {}
	for t in targets:
		scores[t.name] = []
		for e in ensembles:
			scores[t.name].append(sum(e.fitness[t.name].itervalues()))

	return scores

def get_unique_ensembles( ensembles ):

	# initialize the list with the first ensemble
	unique = [ ensembles[0] ]

	# only append ensembles that contain different components
	for e in ensembles:
		for seen in unique:
			if( set(seen.component_names) == set(e.component_names) ):
				break
		else:
			unique.append(e)

	return unique

def set_ensemble_state( args, ensembles, components ):

	try:
		f = open( args.resume, 'r' )
	except IOError:
		print_msg( "\t\tERROR: Could not open ensemble state table \"%s\"" % file )
		return False

	names = components.keys()

	i = 0
	for line in f:
		if(i>len(ensembles)):
			print_msg( "\t\tWARNING: Stopped loading ensemble state file at table %i" % (i+1) )
			break

		# read only the first target (components are the same, only weights different)
		a = line.split()
		if(len(a) != (2*args.size)+4):
			print_msg( "\t\tINFO: Finished reading ensemble state table (%i ensembles loaded)" % (i+1) )
			break

		for j in range(args.size):
			if(not a[j +1] in names):
				print_msg( "\t\tERROR: Component \"%s\" referenced in line %i of ensemble state table not found in loaded components" % (a[j+1],i+1) )
			else:
				ensembles[i].component_names[j] = a[j+1]

		i+=1

	f.close()
	return True



