#!/usr/bin/env python

import argparse
import scipy
import matplotlib as mpl

def run():
	parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

	group0 = parser.add_argument_group('Table specification')
	group0.add_argument('input', 	nargs='+',									help='MESMER restraint output file(s).')
	group0.add_argument('-xCol',	default=1,		metavar='N',	type=int,	help='The column containing the desired component attribute')
	group0.add_argument('-yCol',	default=2,		metavar='N',	type=int,	help='The column to use as y-axis data')

	group1 = parser.add_argument_group('Plot options')
	group1.add_argument('-title',					default='',					help='The title for the output figure')
	group1.add_argument('-xLabel',					default='X',				help='Label for the X axis')
	group1.add_argument('-yLabel',					default='Y',				help='Label for the Y axis')
	group1.add_argument('-backend',					default='Agg',	metavar='Agg',	help='Specify the graphics backend for MPL (only used w/ the -nogui option)')
	group1.add_argument('-plotArgs',	nargs=2,	action='append',	default=[],	metavar='',	help='Specify arguments for matplotlib as ARG VALUE')
	group1.add_argument('-plotProp',	nargs=2,	action='append',	default=[],	metavar='',	help='Set properties for the figure as ARG VALUE')
	group1.add_argument('-figsize',		nargs=2,	default=[6,6],	type=int,	metavar='N',	help='Set figure size and ratio: X Y')
	group1.add_argument('-colors',		nargs='*',	default=[] )

	group3 = parser.add_argument_group('Output options')
	group3.add_argument('-nogui', 	action='store_true',	default=False,	help='Don\'t display image.')
	group3.add_argument('-figure', 					default=None,	help='The file to write the resulting figure to.')

	args = parser.parse_args()

	data = []
	for f in args.input:
		data.append( scipy.genfromtxt( f, usecols=(0,1,2), unpack=True ) )

	# set up the plot figure
	if(args.nogui) and (args.figure):
		mpl.use( args.backend )

	import matplotlib.pyplot as plot

	a = plot.axes( [0.1,0.1,0.85,0.85] )

	args.colors.extend(['r','g','b','c','m','y','k','w'])
	for (i,d) in enumerate(data):
		a.scatter( d[0], d[1], c='k', facecolors='none' )
		a.plot( d[0], d[2], '%s-' % args.colors[i], linewidth=2 )

	plot.title( args.title )
	plot.xlabel( args.xLabel )
	plot.xlim([min(data[0][0]),max(data[0][0])])
	plot.ylabel( args.yLabel )

	b = plot.axes([0.5,0.5,0.43,0.43])

	for (i,d) in enumerate(data):
		if len(data) == 1:
			b.plot( d[0], [0]*len(d[0]), '%s-' % args.colors[i], linewidth=2 )
			b.scatter( d[0], d[1]-d[2], edgecolor='k', facecolors='none' )
		else:
			b.plot( d[0], [0]*len(d[0]), 'k-', linewidth=2 )
			b.scatter( d[0], d[1]-d[2], edgecolor=args.colors[i], facecolors='none' )

	plot.ylabel( r'$Y_{exp}-Y_{fit}$' )
	plot.xlim([min(data[0][0]),max(data[0][0])])

	for (arg,val) in args.plotArgs:
		mpl.rcParams[ arg ] = val

	if(args.figure):
		print "Plotting figure \"%s\"" % args.figure
		plot.savefig( args.figure )

	if(not args.nogui) or (not args.figure):
		plot.show()

if( __name__ == "__main__" ):
	run()