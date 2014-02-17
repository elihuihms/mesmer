import sys
import math
import random
import copy

from scipy					import optimize
from multiprocessing		import Process,Queue

from optimization_functions	import blind_random_min,localized_random_min

def optimize_ratios( args, components, plugins, targets, ensembles, q=None, print_status=True ):
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

	n1,n2 = len(targets),len(ensembles)
	divisor = int(max(n1*n2/100,1))
	for (i,t) in enumerate(targets):
		for (j,e) in enumerate(ensembles):
			if((i*j) % divisor == 0 and print_status):
				sys.stdout.write("\tComponent ratio optimization progress: %i%%\r" % (100.*(i+1)*j/(n1*n2)+1) )
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

	if q != None:
		q.put(ensembles)
		return

	return ensembles

def mp_optimize_ratios( args, components, plugins, targets, ensembles, print_status=True ):
	"""
	A multiprocessing wrapper for the function optimize_ratios.
	See that function's docstrings for more information.

	Returns a copy of the provided ensembles that have had their component ratios optimized
	"""

	# Under Windows, all arguments to Process must be picklable. (http://docs.python.org/2/library/multiprocessing.html#windows)
	# Since we can't pickle the plugin functions, we won't be able multithread w/o some significant changes. Until then, args.threads is set to 1 for Windows environments
	if( args.threads == 1 ): # multithreading disabled
		tmp = copy.deepcopy( ensembles )
		return optimize_ratios( args, components, plugins, targets, tmp, q=None, print_status=print_status )

	q = Queue()
	chunksize = int(math.ceil(len(ensembles) / float(args.threads)))

	# randomize ensemble order so threads should finish processing their chunks in about the same time
	random.shuffle( ensembles )

	procs = []
	for i in range( args.threads ):
		p = Process(target=optimize_ratios, args=(args,components,plugins,targets,ensembles[:chunksize],q,print_status))
		procs.append( p )
		p.start()

		del ensembles[:chunksize] # remove unoptimized ensembles

	for i in range( args.threads ):
		ensembles.extend( q.get() )

	for p in procs:
		p.join()

	return ensembles