import scipy

from mesmer.lib.utility_objects import MESMERUtility

class MakeAttributeSpec(MESMERUtility):
	def __init__(self):
		super(MakeAttributeSpec, self).__init__()
		
		self.parser.add_argument('table', 												help='A file containing tab-delimited statistics of the available components')
		self.parser.add_argument('-nCol',	default=0,		metavar='N',	type=int,	help='The column containing the component names')
		self.parser.add_argument('-dCol',	default=1,		metavar='N',	type=int,	help='The column containing the desired component attribute')
		self.parser.add_argument('-mean',	default=None,					type=float,	help='The value to use as the center of the distribution. Defaults to the mean of the selected dataset.')
		self.parser.add_argument('-stdev',	default=None,					type=float,	help='The width of the distribution. Defaults to the standard deviation of the selected dataset.')
		self.parser.add_argument('-uniform',	default=False,	action='store_true',		help='Use a uniform instead of gaussian distribution.')
		self.parser.add_argument('-intersect',default=None,	metavar='<SPEC>',			help='Multiply an existing target specification with this one.')
		self.parser.add_argument('-add',		default=None,	metavar='<SPEC>',			help='Add an existing target specification to this one.')
		self.parser.add_argument('-subtract',default=None,	metavar='<SPEC>',			help='Subtract an existing target specification from this one.')
		self.parser.add_argument('-out',		required=True,								help='The path to which the target specification should be written.')

	def run(self,args):
		if(args.table==None):
			return 1,"You must provide a component attribute table"

		# table 0 = names
		# table 1 = data values
		table = scipy.genfromtxt( args.table, usecols=(args.nCol,args.dCol), dtype=str, unpack=True )
		n = len(table[0])
		names = list(table[0])

		# convert data strings to floats
		values = [0.0]*n
		for i in range(n):
			values[i] = float(table[1][i])

		# set default values for mean, stdev if not specified
		if( args.mean == None ):
			args.mean = scipy.mean( values )
		if( args.stdev == None ):
			args.stdev = scipy.std( values )

		# extract component weighting from a previously created specification file
		prev = [1.0]*n
		if (args.intersect) or (args.add) or (args.subtract) :
			if( args.intersect ):
				tmp = scipy.genfromtxt( args.intersect, dtype=str, usecols=(0,1), unpack=True )
			elif( args.add ):
				tmp = scipy.genfromtxt( args.add, dtype=str, usecols=(0,1), unpack=True )
			elif( args.subtract ):
				tmp = scipy.genfromtxt( args.subtract, dtype=str, usecols=(0,1), unpack=True )

			tmp = (list(tmp[0]),list(tmp[1]))
			for i in range(n):
				try:
					k = names.index(tmp[0][i])
				except:
					return 1,"Existing target specification contains a component (%s) that does not exist in the provided attribute table." % tmp[0][i]
				prev[k] = float(tmp[1][i])

		weights = [0.0]*n
		for i in range(n):
			if( args.uniform ):
				if (values[i] < args.mean+args.stdev) and (values[i] > args.mean-args.stdev):
					weights[i] = 1.0
			else:
				weights[i] = (1 / (args.stdev * scipy.sqrt(2*scipy.pi))) * scipy.exp( -0.5 * ((values[i] - args.mean) / args.stdev)**2 )

		# normalize weights
		total = sum(weights)
		for i in range(n):
			weights[i] = weights[i] / total

		for i in range(n):
			if( args.intersect ):
				weights[i] = weights[i]*prev[i]
			elif( args.add ):
				weights[i] = weights[i]+prev[i]
			elif( args.subtract ):
				weights[i] = weights[i]-prev[i]

		# normalize weights again
		total = sum(weights)
		for i in range(n):
			weights[i] = weights[i] / total

		f = open( args.out, 'w' )
		for i in range(n):
			f.write( "%s\t%.3E\n" % (names[i],weights[i]) )
		f.close()
		
		return 0