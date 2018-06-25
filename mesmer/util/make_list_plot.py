import scipy
import matplotlib as mpl

from mesmer.lib.utility_objects import MESMERUtility

class MakeLISTPlot(MESMERUtility):
	def __init__(self):
		super(MakeLISTPlot, self).__init__()

		group0 = self.parser.add_argument_group('Table specification')
		group0.add_argument('input', 		nargs='+',					help='MESMER restraint output file(s).')
		group0.add_argument('-xCol',	default=1,		metavar='N',	type=int,	help='The column containing the desired component attribute')
		group0.add_argument('-yCol',	default=2,		metavar='N',	type=int,	help='The column to use as y-axis data')

		group1 = self.parser.add_argument_group('Plot options')
		group1.add_argument('-title',					default='',				help='The title for the output figure')
		group1.add_argument('-xLabel',					default='',				help='The label for the x-axis')
		group1.add_argument('-yLabel',					default='',				help='The label for the y-axis')
		group1.add_argument('-backend',					default='Agg',	metavar='Agg',	help='Specify the graphics backend for MPL (only used w/ the -nogui option)')
		group1.add_argument('-plotArgs',	nargs=2,	action='append',	default=[],	metavar='',	help='Specify arguments for matplotlib as ARG VALUE')
		group1.add_argument('-plotProp',	nargs=2,	action='append',	default=[],	metavar='',	help='Set properties for the figure as ARG VALUE')
		group1.add_argument('-figsize',		nargs=2,	default=[6,6],	type=int,	metavar='N',	help='Set figure size and ratio: X Y')
		group1.add_argument('-pointScale',				default=40,		type=int,	metavar='20',	help='Change the scaling of the attribute scatter plot points')
		group1.add_argument('-colors',		nargs='*',	default=[] )

		group2 = self.parser.add_argument_group('Output options')
		group2.add_argument('-nogui', 	action='store_true',	default=False,	help='Don\'t display image.')
		group2.add_argument('-figure', 					default=None,	help='The file to write the resulting figure to.')

	def run(self,args):
		# generate master data lists
		data = [None]*len(args.input)
		for (i,f) in enumerate(args.input):
			data[i] = [None,None]
			(data[i][0],data[i][1]) = scipy.genfromtxt( f, dtype=float, usecols=(args.xCol,args.yCol), unpack=True )
			if (True in scipy.isnan(data[i][0])) or (True in scipy.isnan(data[i][1])):
				return 1,"Failed reading valid numbers from specified column of \"%s\". Perhaps -xCol or -yCol are incorrect?" % (f)

		# set up the plot figure
		if(args.nogui) and (args.figure):
			mpl.use( args.backend )

		import matplotlib.pyplot as plot
		import matplotlib.gridspec as gridspec

		fig = plot.figure(1, figsize=(args.figsize[0],args.figsize[1]))
		gs1 = gridspec.GridSpec(2,1,height_ratios=[0.75,0.2])
		ax1 = fig.add_subplot( gs1[0] )
		ax2 = fig.add_subplot( gs1[1] )
		plot.suptitle( args.title )

		xMax = data[0][0][0]
		xMin = data[0][0][0]
		lMax = 0
		for d in data:
			xMax = max( [xMax,max(d[0])] )
			xMax = max( [xMax,max(d[1])] )
			xMin = min( [xMin,min(d[0])] )
			xMin = min( [xMin,min(d[1])] )
			lMax = max( [lMax,len(d[0])] )

		ax1.plot( [xMin,xMax], [xMin,xMax], 'k-' )
		ax1.set_xlim( [xMin,xMax] )
		ax1.set_ylim( [xMin,xMax] )
		ax1.set_xlabel( args.xLabel )
		ax1.set_ylabel( args.yLabel )

		ax2.plot( [0,lMax], [0,0], 'k-' )
		ax2.set_xlim( [0,lMax] )

		args.colors.extend(['b','g','r','c','m','y','k','w'])
		for (i,d) in enumerate(data):
			ax1.scatter( d[0], d[1], c=args.colors[i], edgecolors='none' )
			ax2.scatter( [j for j in range(len(d[0]))], d[0] - d[1], c=args.colors[i], edgecolors='none' )

		for (arg,val) in args.plotArgs:
			mpl.rcParams[ arg ] = val

		if(args.figure):
			print "Plotting figure \"%s\"" % args.figure
			plot.savefig( args.figure )

		if(not args.nogui) or (not args.figure):
			plot.show()
			
		return 0