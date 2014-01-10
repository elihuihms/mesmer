#!/usr/bin/env python

import argparse
import sys
import os
import scipy

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.utility_functions	import mean_stdv
from lib.output_parsers		import get_ensembles_from_state

def run():
	parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

	group0 = parser.add_argument_group('Input options')
	group0.add_argument('table',	default=None,	metavar='<TABLE>',			help='A file containing tab-delimited statistics of the available components')
	group0.add_argument('state', 	default=None,	metavar='<STATE>',			help='A MESMER ensemble state file')
	group0.add_argument('-nCol',	default=0,		metavar='N',	type=int,	help='The column containing the component names')
	group0.add_argument('-dCols',	nargs='+',	default=[1],		metavar='N',	type=int,	help='Column numbers containing the attributes to sort ensembles by')
	#group0.add_argument('-dVals',	nargs='*',	default=None,		metavar='N',	type=float,	help='Attribute values to sort ensembles by')

	group1 = parser.add_argument_group('Output options')
	group1.add_argument('-N',	default=None,	metavar='N',	type=int,		help='Specify the number of ensembles to print. Defaults to all')
	group1.add_argument('-R',	action='store_true', default=False,				help='Reverse sort')
	group1.add_argument('-Pall',	action='store_true',	default=False,		help='Print attribute for each component')

	group2 = parser.add_argument_group('Ordering options')
	group2.add_argument('-avg',			action='store_true',				help='Sort by the ensemble\'s average specified attribute')
	group2.add_argument('-deviation',	type=float,	metavar='N',			help='Sort by the ensemble\'s deviation from the specified attribute')
	group2.add_argument('-totalRSD',	action='store_true',				help='Sort by ensemble\'s total RSD across the specified attributes')

	args = parser.parse_args()

	if( not args.table ):
		print "ERROR: Must specify an attribute table."
		exit()

	if( not args.state ):
		print "ERROR: Must specify a state table."
		exit()

	tmp = scipy.genfromtxt( args.table, dtype=str, unpack=True )

	try:
		component_names = list( tmp[args.nCol] )
	except:
		print "ERROR: Couldn't read component names from column %i of the attribute table" % args.nCol

	component_attributes = []
	for col in args.dCols:
		try:
			component_attributes.append( map(float, tmp[col]) )
		except:
			print "ERROR: Couldn't read component values from column %i of the attribute table" % i

	try:
		ensembles = get_ensembles_from_state( args.state, unique=True )
	except Exception as e:
		print "ERROR: Couldn't read ensembles from state file. Reason: %s" % (e)
		exit()

	ensemble_attributes,ensemble_weights = [], []
	for e in ensembles:
		ensemble_attributes.append( [] )
		ensemble_weights.append( e['weights'] )

		for col in range(len(args.dCols)):
			ensemble_attributes[-1].append( [] )

			for name in e['components']:
				try:
					row = component_names.index( name )
				except ValueError:
					print "ERROR: Could not find component \"%s\" in the attribute table" % name
					exit()

				ensemble_attributes[-1][ col ].append( component_attributes[ col ][ row ] )

	# calculate the ensemble's value for the first attribute specified by -dCol
	average_attributes = []
	for (i,ensemble) in enumerate(ensemble_attributes):
		average_attributes.append( 0.0 )
		for (j,value) in enumerate(ensemble[0]):
			average_attributes[-1] += value * ensemble_weights[i][j]

	if( args.Pall ):
		print "#\tN\tfitness\t[components]\t[attributes]"
		for (i,e) in enumerate( ensembles ):
			order = scipy.argsort( ensemble_attributes[i][0] )
			names = scipy.take( e['components'], order )
			attrs = map(str,scipy.take(ensemble_attributes[i][0], order) )
			print "%i\t%i\t%.3f\t%s\t%s" % ( i, e['count'], e['fitness'], ' '.join(names), ' '.join(attrs) )
		sys.exit(0)

	elif( args.avg ):
		if( len(args.dCols) > 1 ):
			print "For sorting by average attribute, specify a single attribute column."
			exit()
		sortable = average_attributes

	elif( args.deviation ):
		if( len(args.dCols) > 1 ):
			print "For sorting by deviation from a specified value, specify a single attribute column."
			exit()

		sortable = []
		for i in range(len(average_attributes)):
			sortable.append( average_attributes[i] - args.deviation )

	elif( args.totalRSD ):
		sortable = []
		for ensemble in ensemble_attributes:
			sortable.append( 0.0 )

			for attributes in ensemble:
				(mean,stdev) = mean_stdv(attributes)
				sortable[-1] += stdev/mean # RSD, normalized standard deviation
	else:
		sortable = range(len(ensemble_attributes))

	order = scipy.argsort( sortable )

	if( args.R):
		order = order[::-1]

	indexes = scipy.take( range(len(ensembles)), order )
	sortable = scipy.take( sortable, order )

	print "#\tN\tsort\tfitness\t[components]"
	for (i,e) in enumerate(scipy.take( ensembles, order )):
		print "%i\t%i\t%.3f\t%.3f\t%s" % ( indexes[i], e['count'], sortable[i], e['fitness'], ' '.join(sorted(e['components'])) )

if( __name__ == "__main__" ):
	run()



