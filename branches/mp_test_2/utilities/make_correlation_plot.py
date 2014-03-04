#!/usr/bin/env python

import argparse
import scipy
import matplotlib as mpl

from colorsys import hsv_to_rgb

def run():
	parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

	group0 = parser.add_argument_group('Table specification')
	group0.add_argument('input', nargs='+',												help='MESMER component correlation file and optionally statistics file.')

	group1 = parser.add_argument_group('Plot options')
	group1.add_argument('-title',					default='',					help='The title for the output figure')
	group1.add_argument('-size',					default=10,		type=int,	metavar='N',	help='Specify the graphics backend for MPL (only used w/ the -nogui option)')
	group1.add_argument('-backend',					default='Agg',	metavar='Agg',	help='Specify the graphics backend for MPL (only used w/ the -nogui option)')
	group1.add_argument('-plotArgs',	nargs=2,	action='append',	default=[],	metavar='',	help='Specify arguments for matplotlib as ARG VALUE')
	group1.add_argument('-plotProp',	nargs=2,	action='append',	default=[],	metavar='',	help='Set properties for the figure as ARG VALUE')
	group1.add_argument('-figsize',		nargs=2,	default=[6,6],	type=int,	metavar='N',	help='Set figure size and ratio: X Y')

	group2 = parser.add_argument_group('Highlight options')
	group2.add_argument('-highlight',	nargs='*',	default=[],					metavar="Name",	help='Highlight specific conformers w/ red colorization')

	group3 = parser.add_argument_group('Output options')
	group3.add_argument('-nogui', 	action='store_true',	default=False,	help='Don\'t display image.')
	group3.add_argument('-figure', 					default=None,	help='The file to write the resulting figure to.')

	args = parser.parse_args()

	if(len(args.input)<1):
		print "You must specify at least a correlation input file"
		exit()

	corr = scipy.genfromtxt( args.input[0], unpack=True, dtype=None, skip_header=1 )
	last = min(args.size,len(corr))

	weights = None
	if(len(args.input)>1):
		tmp = scipy.genfromtxt( args.input[1], unpack=True, dtype=None, skip_header=2 )

		weights = []
		for i in range(args.size):
			if(i<len(tmp)):
				weights.append(	tmp[i][3] )
			else:
				weights.append( 0 )

	data, names = [], []
	for i in range(args.size):
		if(i<last):
			names.append( corr[i][0] )
			data.append( list(corr[i])[1:args.size+1] )
		else:
			names.append( '' )
			data.append( [0]*(args.size+1) )

	# set up the plot figure
	if(args.nogui) and (args.figure):
		mpl.use( args.backend )

	import matplotlib.pyplot as plot

	# make dummy plot for colorbar
	Z = [[0,0],[0,0]]
	CS3 = plot.contourf(Z,range(101))
	CS3.set_cmap(plot.cm.gray)
	plot.gray()
	plot.clf()

	x,y,s,c = [],[],[],[]
	for i in range(last):
		for j in range(last):
			x.append( i )
			y.append( j )
			s.append( data[i][j] * (5000/args.size) )

			if(weights == None):
				c.append( (0.5,0.5,0.5) )
			elif(i==j):
				if(str(names[i]) in args.highlight):
					c.append( (max(0,1-weights[i]),0,0) )
				else:
					c.append( [max(0,1-weights[i])]*3 )
			else:
				if(str(names[i]) in args.highlight and str(names[j]) in args.highlight):
					c.append( (max(0,1-(weights[i]+weights[j])),0,0) )
				else:
					c.append( [max(0,1-(weights[i]+weights[j]))]*3 )

	plot.scatter( x, y, s=s, c=c )

	#
	plot.title( args.title )
	plot.xticks( range(args.size), names, rotation=90)
	plot.yticks( range(args.size), names)
	plot.subplots_adjust(bottom=0.2)

	#
	cbar = plot.colorbar(CS3,ticks=[100,0])
	cbar.ax.set_yticklabels(['0','1'])
	cbar.ax.set_ylabel('Weighting')
	#cbar.ax.yaxis.get_offset_text().set_position((-10,0))

	#
	ax = plot.gca()
	ax.set_aspect('equal')

	#
	ax.xaxis.set_label_position("top")
	plot.xlabel("Relative Correlation")
	ax.xaxis.grid()
	ax.xaxis.set_ticks(range(last))
	ax.set_xlim( [-1,args.size] )

	#
	ax.yaxis.set_label_position("right")
	plot.ylabel("Absolute Correlation")
	ax.yaxis.grid()
	ax.yaxis.set_ticks(range(last))
	ax.set_ylim( [-1,args.size] )

	for t in ax.xaxis.get_major_ticks():
		t.tick1On = False
		t.tick2On = False
	for t in ax.yaxis.get_major_ticks():
		t.tick1On = False
		t.tick2On = False

	#
	for (arg,val) in args.plotArgs:
		mpl.rcParams[ arg ] = val

	if(args.figure):
		print "Plotting figure \"%s\"" % args.figure
		plot.savefig( args.figure )

	if(not args.nogui) or (not args.figure):
		plot.show()

if( __name__ == "__main__" ):
	run()