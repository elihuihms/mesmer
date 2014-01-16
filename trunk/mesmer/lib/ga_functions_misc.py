import os
import os.path
import sys
import random
import math

from exceptions				import *
from ensemble_objects		import mesEnsemble
from utility_functions		import print_msg,mean_stdv

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



