#!/usr/bin/env python

import argparse
import scipy
import matplotlib as mpl
import math
import random
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.output_parsers		import get_ensembles_from_state
from lib.utility_functions	import extract_list_elements

def run():
	parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

	#

	def make_named_vectors( tbl ):
		n,m = len(tbl), len(tbl[0])
		tbl = list(tbl)
		tbl[0] = list(tbl[0])
		for i in range(1,n):
			tbl[i] = map( float, tbl[i] )
		return tbl

	#

	group0 = parser.add_argument_group('Table specification')
	group0.add_argument('tables', 	nargs='+',		metavar='<FILE>.tbl',		help='File(s) containing tab-delimited statistics of the available components')
	group0.add_argument('-nCol',	default=0,		metavar='0',	type=int,	help='The column containing the component names')
	group0.add_argument('-xCol',	default=1,		metavar='1',	type=int,	help='The column containing the desired component attribute')
	group0.add_argument('-yCol',	default=2,		metavar='2',	type=int,	help='The column to use as y-axis data')
	group0.add_argument('-zCol',	default=None,	metavar='3',	type=int,	help='The column to use as z-axis data')
	group0.add_argument('-subsample',			default=1,	type=float,			help='Randomly subsample selected data by a percentage.')

	group1 = parser.add_argument_group('Plot options')
	group1.add_argument('-title',					default='',				help='The title for the output figure')
	group1.add_argument('-xLabel',					default='',				help='The label for the x-axis')
	group1.add_argument('-yLabel',					default='',				help='The label for the y-axis')
	group1.add_argument('-zLabel',					default='',				help='The label for the z-axis')
	group1.add_argument('-backend',					default='Agg',	metavar='Agg',	help='Specify the graphics backend for MPL (only used w/ the -nogui option)')
	group1.add_argument('-plotArgs',	nargs=2,	action='append',	default=[],	metavar='',	help='Specify arguments for matplotlib as ARG VALUE')
	group1.add_argument('-plotProp',	nargs=2,	action='append',	default=[],	metavar='',	help='Set properties for the figure as ARG VALUE')
	group1.add_argument('-figsize',		nargs=2,	default=[6,6],	type=int,	metavar='N',	help='Set figure size and ratio: X Y')
	group1.add_argument('-axes',		nargs=4,	default=None,	type=float,	metavar='N',	help='The scales for the axes: xmin, xmax, ymin, ymax')
	group1.add_argument('-pointScale',				default=20,		type=int,	metavar='20',	help='Set scaling of the component plot points')
	group1.add_argument('-pointColor',	nargs=4,	default=[0,0,0,0.1], type=float,	metavar='N',	help='Set color (R G B A) of componenent plot points')

	group2 = parser.add_argument_group('Component statistic overlay options')
	group2.add_argument('-stats',	default=None,	metavar='component_statistics_*.tbl',		help='A MESMER ensemble statistics file')
	group2.add_argument('-statPtWidth',				default=3,		type=int,	metavar='3.0',	help='Change the width of the selected component plot circles')
	group2.add_argument('-statPtColor',	nargs=4,	default=[0.0,0.5,1.0,1.0],	type=float,	metavar='N',	help='Specifies the RGB color shading (0-1) to be used for the ensemble statistics overlay')
	group2.add_argument('-statPtScale',				default=10,		type=int,	metavar='20',	help='Set scaling of the component statistics plot points')
	group2.add_argument('-statNorm',	action='store_true', default=False,				help='Normalize variable color saturation for component prevalence')
	group2.add_argument('-statSame',	action='store_true', default=False,				help='Do not use variable color saturation for component prevalence')
	group2.add_argument('-statWeight',				default=-1.0,	type=float,			help='When plotting MESMER statistics, drop components weighted lower than this amount')
	group2.add_argument('-statPrevalence',			default=-1.0,	type=float,			help='When plotting MESMER statistics, drop components with prevalences lower than this amount')
	group2.add_argument('-statSubsample',			default=1,		type=float,			help='Randomly subsample selected conformers by a percentage.')

	group3 = parser.add_argument_group('Ensemble statistics overlay options')
	group2.add_argument('-ensembles',			default=None,	metavar='ensembles_*.tbl',	help='A MESMER ensemble state file')
	group3.add_argument('-ensembleSolutions',	default=4,		type=int,	metavar='N',	help='The number of unique ensemble solutions to show')
	group3.add_argument('-ensemblePtScale',		default=10,		type=int,	metavar='20',	help='Set scaling of the highlight plot circles')
	group3.add_argument('-ensemblePtWidth',		default=3,		type=int,	metavar='3.0',	help='Set the width of the highlight plot circles')
	group3.add_argument('-ensemblePtColors',		nargs='*',	default=[],		metavar='C',	help='A series of matplotlib colors to use for highlighting different ensemble solutions')
	group3.add_argument('-ensembleHighlight',	nargs='*',	default=[],	type=int,	metavar='N',	help='Highlight unique ensemble IDs provided by get_ensemble_stats')

	group4 = parser.add_argument_group('Synthetic target specification overlay options')
	group4.add_argument('-spec',	default=None,	metavar='<SPEC>.spec',		help='A specification file')
	group4.add_argument('-specColor',	nargs=4,	default=[1.0,0.5,0.0,1.0],	type=float,	metavar='N',	help='Specifies the RGB color shading (0-1) to be used for the specification overlay')
	group4.add_argument('-specWeight',				default=-1.0,	type=float,			help='When plotting target specifications, drop components weighted lower than this amount')
	group4.add_argument('-specLog',		action='store_true', default=False,				help='Use log of spec weight for shading')

	group5 = parser.add_argument_group('Highlighting overlay options')
	group5.add_argument('-highlight',		nargs='*',	default=[],		metavar='NAME',	help='List of component names to highlight')
	group5.add_argument('-highlightSize',	default=20,		type=int,	metavar='20',	help='Set scaling of the highlight plot circles')
	group5.add_argument('-highlightWidth',	default=3,		type=int,	metavar='3.0',	help='Set the width of the highlight plot circles')
	group5.add_argument('-highlightColor',	nargs=3,	default=[1.0,0.0,0.0],	type=float,	metavar='N',	help='Set color (R G B) to use for highlighting')

	group6 = parser.add_argument_group('Output options')
	group6.add_argument('-nogui', 	action='store_true',	default=False,	help='Don\'t display image.')
	group6.add_argument('-figure', 					default=None,	help='The file to write the resulting figure to.')

	args = parser.parse_args()

	if(len(args.ensembleHighlight)>0 and not args.ensembles):
		print "ERROR: To highlight a specific ensemble ID please provide an ensemble state file."
		sys.exit(1)

	plot_data = [ [],[],[],[] ] # generate master data lists
	for t in args.tables:
		if( args.zCol ):
			tmp = make_named_vectors(scipy.genfromtxt( t, usecols=(args.nCol,args.xCol,args.yCol,args.zCol), dtype=str, unpack=True ))
		else:
			tmp = make_named_vectors(scipy.genfromtxt( t, usecols=(args.nCol,args.xCol,args.yCol,args.yCol), dtype=str, unpack=True ))

		for i in range(len(plot_data)):
			plot_data[i].extend( tmp[i] )

	# read target specification, if provided
	if( args.spec ):
		spec_data = make_named_vectors(scipy.genfromtxt( args.spec, usecols=(0,1), dtype=str, unpack=True ))
		spec_data.extend( [[],[],[]] )
		for (i,n) in enumerate(spec_data[0]): # check names against provided component names and retrieve coordinates

			if(args.specLog):
				spec_data[1][i] = 1/(-1.0 * math.log(spec_data[1][i]))

			try:
				k = plot_data[0].index(n)
			except:
				print "ERROR: Target specification contains a component (%s) that does not exist in the attribute table." % n
				sys.exit(1)

			spec_data[2].append( plot_data[1][k] )
			spec_data[3].append( plot_data[2][k] )
			spec_data[4].append( plot_data[3][k] )

	# read component statistics file, if provided
	if( args.stats ):
		stats_data = [ [],[],[], [],[],[] ]

		f = open( args.stats, 'r' )
		line = f.readline()
		while(line):
			line = f.readline().strip()
			if(line == ''):
				break

			a = line.split()
			try:
				k = plot_data[0].index(a[0])
			except:
				print "ERROR: Ensemble statistics file contains a component (%s) that does not exist in the attribute table." % a[0]
				sys.exit(1)

			stats_data[0].append( a[0] )
			stats_data[1].append( float(a[1]) )
			stats_data[2].append( float(a[3]) )
			stats_data[3].append( plot_data[1][k] )
			stats_data[4].append( plot_data[2][k] )
			stats_data[5].append( plot_data[3][k] )

	if( args.ensembles ):
		state_data = [ [],[],[], [],[],[] ]

		try:
			ensemble_stats = get_ensembles_from_state( args.ensembles, unique=True )
		except Exception as e:
			print "ERROR: Could not load ensemble information from state file. Reason: %s" % (e)
			sys.exit(1)

		if( len(args.ensembleHighlight)>0 ):
			id_list = args.ensembleHighlight
		else: # randomly select a number of solutions
			id_list = range(min(args.ensembleSolutions, len(ensemble_stats) ))
			random.shuffle(ensemble_stats)

		args.ensemblePtColors.extend( ['r','g','b','c','m','y','w' ] )
		for (i,id) in enumerate(id_list):
			for (j,name) in enumerate( ensemble_stats[id]['components'] ):
				try:
					k = plot_data[0].index(name)
				except ValueError:
					print "ERROR: the component \"%s\" from the ensemble state file doesn't exist in the attribute table." % (name)
					sys.exit(1)

				state_data[0].append( name )
				state_data[1].append( args.ensemblePtColors[i % len(args.ensemblePtColors)] )
				state_data[2].append( 30*args.ensemblePtScale*ensemble_stats[id]['weights'][j] )
				state_data[3].append( plot_data[1][k] )
				state_data[4].append( plot_data[2][k] )
				state_data[5].append( plot_data[3][k] )

	if( len(args.highlight) > 0 ):
		highlight_data = [ [], [],[],[] ]

		for name in args.highlight:
			try:
				k = plot_data[0].index(name)
			except ValueError:
				print "ERROR: the component \"%s\" from highlight list doesn't exist in the attribute table." % (name)
				sys.exit(1)

			highlight_data[0].append( name )
			highlight_data[1].append( plot_data[1][k] )
			highlight_data[2].append( plot_data[2][k] )
			highlight_data[3].append( plot_data[3][k] )

	# now that we have coords saved to the various overlays, subsample data if necessary
	keys = random.sample( range(len(plot_data[0])), int(len(plot_data[0])*args.subsample) )
	for i in range(len(plot_data)):
		plot_data[i] = extract_list_elements( plot_data[i], keys )

	#
	# plotting now
	#

	# set up the plot figure
	if(args.nogui) and (args.figure):
		mpl.use( args.backend )

	import matplotlib.pyplot as plot # have to import *after* mpl
	fig = plot.figure(1, figsize=(args.figsize[0],args.figsize[1]))

	# obtain plot axes
	if(args.zCol):
		from mpl_toolkits.mplot3d import Axes3D
		ax = Axes3D(fig)
		ax = fig.add_subplot(111, projection='3d')
	else:
		ax = fig.add_subplot(111)
		#ax = plot.axes( [0.1,0.1,0.85,0.65] )
		#ax = plot.axes( [0.1,0.1,0.70,0.80] )

	if( len(plot_data[1]) > 0 ):
		if(args.zCol):
			ax.scatter( plot_data[1], plot_data[2], plot_data[3],	facecolor=args.pointColor, edgecolors='none', s=args.pointScale, zorder=0 )
		else:
			ax.scatter( plot_data[1], plot_data[2],					facecolor=args.pointColor, edgecolors='none', s=args.pointScale, zorder=0 )

	if( args.spec ):
		keys = [] # discard components with weighting lower than specified
		for (i,w) in enumerate(spec_data[1]):
			if(w > args.specWeight):
				keys.append(i)
		for i in range(len(spec_data)):
			spec_data[i] = extract_list_elements( spec_data[i], keys )

		o = scipy.argsort( spec_data[1][:] ) # sort components by weight, so that more heavily-weighted will be on top
		for i in range(len(spec_data)) :
			spec_data[i] = list(scipy.take( spec_data[i], o ))

		m = max(spec_data[1]) # generate coloring for specification overlay points
		for i in range(len(spec_data[0])):
			spec_data[1][i] = (
				spec_data[1][i]/m*args.specColor[0],
				spec_data[1][i]/m*args.specColor[1],
				spec_data[1][i]/m*args.specColor[2],
				args.specColor[3])

		if( args.zCol):
			ax.scatter( spec_data[2],spec_data[3],spec_data[4],	facecolors=spec_data[1], edgecolors='none', s=args.pointScale, zorder=1 )
		else:
			ax.scatter( spec_data[2],spec_data[3],				facecolors=spec_data[1], edgecolors='none', s=args.pointScale, zorder=1 )

	if( args.stats ):
		keys = [] # discard components with prevalence or weight lower than specified
		for i in range(len(stats_data[1])):
			if(stats_data[1][i] > args.statPrevalence) and (stats_data[2][i] > args.statWeight):
				keys.append(i)
		for i in range(len(stats_data)):
			stats_data[i] = extract_list_elements( stats_data[i], keys )

		keys = random.sample( range(len(stats_data[0])), int(len(stats_data[0])*args.statSubsample) ) # subsample list elements
		for i in range(len(stats_data)):
			stats_data[i] = extract_list_elements( stats_data[i], keys )

		o = scipy.argsort( stats_data[1][:] ) # sort components by prevalence
		for i in range(len(stats_data)):
			stats_data[i] = list(scipy.take( stats_data[i], o ))

		m = max(stats_data[1])
		for i in range(len(stats_data[0])):

			if(args.statSame):
				stats_data[1][i] = (
					args.statPtColor[0],
					args.statPtColor[1],
					args.statPtColor[2],
					args.statPtColor[3])
			elif(args.statNorm):
				stats_data[1][i] = (
					stats_data[1][i]/m*args.statPtColor[0],
					stats_data[1][i]/m*args.statPtColor[1],
					stats_data[1][i]/m*args.statPtColor[2],
					args.statPtColor[3])
			else:
				stats_data[1][i] = (
					stats_data[1][i]/100.0*args.statPtColor[0],
					stats_data[1][i]/100.0*args.statPtColor[1],
					stats_data[1][i]/100.0*args.statPtColor[2],
					args.statPtColor[3])

			stats_data[2][i] = stats_data[2][i]*30*args.statPtScale

		if( args.zCol ):
			ax.scatter( stats_data[3],stats_data[4],stats_data[5], 	edgecolors=stats_data[1], s=stats_data[2], zorder=2, facecolors='none', linewidth=args.statPtWidth )
		else:
			ax.scatter( stats_data[3],stats_data[4],				edgecolors=stats_data[1], s=stats_data[2], zorder=2, facecolors='none', linewidth=args.statPtWidth )

	if( args.ensembles ):
		if( args.zCol ):
			ax.scatter( state_data[3], state_data[4], state_data[5],	edgecolors=state_data[1], s=state_data[2], zorder=3, facecolors='none', linewidth=args.ensemblePtWidth )
		else:
			ax.scatter(	state_data[3], state_data[4], 					edgecolors=state_data[1], s=state_data[2], zorder=3, facecolors='none', linewidth=args.ensemblePtWidth )

	if( len(args.highlight) > 0 ):
		if( args.zCol ):
			ax.scatter( highlight_data[1], highlight_data[2], highlight_data[3],	edgecolors=args.highlightColor, s=20*args.highlightSize, zorder=4, facecolor='none', linewidth=args.highlightWidth )
		else:
			ax.scatter( highlight_data[1], highlight_data[2], 						edgecolors=args.highlightColor, s=20*args.highlightSize, zorder=4, facecolor='none', linewidth=args.highlightWidth )

	for (arg,val) in args.plotArgs:
		mpl.rcParams[ arg ] = val

	# set plot options
	ax.set_title( args.title )
	ax.set_xlabel( args.xLabel )
	ax.set_ylabel( args.yLabel )

	if(args.zCol):
		ax.set_zlabel( args.zLabel )

	if(args.axes):
		ax.axis( args.axes )

	#t = {}
	#for (arg,val) in args.plotProp:
	#	t[arg] = val
	#	plot.setp( *t )

	if(args.figure):
		print "Plotting figure \"%s\"" % args.figure
		plot.savefig( args.figure )

	if(not args.nogui) or (not args.figure):
		plot.show()

if( __name__ == "__main__" ):
	run()