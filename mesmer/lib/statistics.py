import copy
import random

from mesmer.errors import *
from mesmer.misc import mean_stdv

def get_ratio_stats( targets, ensembles ):
	"""
	Return the components and their weights in the provided ensembles

	Arguments:
	targets		- list of mesTargets ensembles have been fitted against
	ensembles	- list of ensembles to run error estimation on
	"""
	#unique = get_unique_ensembles( ensembles )

	# make a list of the components observed in the unique ensembles
	#components = []
	#for e in unique:
	#	for c in e.component_names:
	#		if( not c in components ):
	#			components.append( c )
	#		else:
	#			break

	# go through *all* ensembles and obtain weights for each component
	component_weights = {}
	for t in targets:
		component_weights[t.name] = {}

		for e in ensembles:
			for (i,c) in enumerate(e.component_names):
				if( c in component_weights[t.name] ):
					component_weights[t.name][c].append( e.ratios[t.name][i] )
				else:
					component_weights[t.name][c] = [ e.ratios[t.name][i] ]

	return component_weights

def get_component_correlations( args, ensembles ):
	"""
	Generate an NxN correlation table of the components present in the ensemble population

	Arguments:
	args		- MESMER argument parameters
	ensembles	- list of ensembles to generate the correlation map for
	"""

	# generate an initial dict of components
	component_counts = {}
	for e in ensembles:
		for name in e.component_names:
			if (name in component_counts):
				component_counts[name]+= 1
			else:
				component_counts[name] = 1

	n = len(ensembles)
	# filter out all components that are lightly-populated
	for name,count in component_counts.items():
		if(float(component_counts[name])/n*100.0 < args.Pcorr):
			del component_counts[name]

	# sort to make most heavily populated first
	names = sorted(component_counts, key=component_counts.get, reverse=True)

	# initialize correlation table
	m = len(names)
	relative_correlations = [[0] * m for i in range(m)]
	absolute_correlations = [[0] * m for i in range(m)]

	# count all examples of the correlation between components in the ensemble pool
	for e in ensembles:
		for i in range(m):
			for j in range(m):
				if(names[i] in e.component_names) and (names[j] in e.component_names):
					relative_correlations[i][j] += 1.0/component_counts[names[j]]
					absolute_correlations[i][j] += 1.0/n

	return (names,relative_correlations,absolute_correlations)

def get_restraint_stats( args, targets, ensembles ):
	"""
	Generate the per-restraint scores for the provided ensembles

	Arguments:
	args		- MESMER argument parameters
	targets		- list of mesTargets ensembles have been fitted against
	ensembles	- list of ensembles to run error estimation on
	"""

	# initialize the return dict structure
	stats = {}
	for r in targets[0].restraints:
		stats[r.type] = {}
		for t in targets:
			stats[r.type][t.name] = []

	# extract the fitness values from the ensembles
	for t in targets:
		for r in targets[0].restraints:
			for e in ensembles:
				stats[r.type][t.name].append(e.fitness[t.name][r.type])

	#  replace the return dict values with the best ensemble restraint score, mean and stdev
	for r in targets[0].restraints:
		for t in targets:
			(mean,stdev) = mean_stdv( stats[r.type][t.name] )
			stats[r.type][t.name] = (ensembles[0].fitness[t.name][r.type],mean,stdev)

	return stats
