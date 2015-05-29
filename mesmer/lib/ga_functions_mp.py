import sys
import math
import random
import copy

from scipy					import optimize
from multiprocessing		import Process,Queue

from optimization_functions	import blind_random_min,localized_random_min

def mp_optimize_setup( args, plugins, targets, components ):

	

def mp_optimize_ratios( ensembles, print_status=True ):


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