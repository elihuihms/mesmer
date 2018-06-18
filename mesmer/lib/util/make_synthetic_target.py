import os
import scipy

from lib.utility_objects import MESMERUtility

class MakeSyntheticTarget(MESMERUtility):
	def __init__(self):
		super(MakeSyntheticTarget, self).__init__()

		self.parser.add_argument('-target',		action='append',	required=True,					metavar='FILE',		help='Target file to use as template')
		self.parser.add_argument('-components',	action='append',	required=True,	nargs='*',		metavar='FILE/DIR',	help='MESMER component files or directory ')
		self.parser.add_argument('-spec',							required=True,					metavar='SPEC',		help='The synthetic target specification file')
		self.parser.add_argument('-dir',							default='./',					metavar='./',		help='Directory to write synthetic data to')
		self.parser.add_argument('-scratch',						default=None)

	def run(self,args):
		args.dbm = False
		args.plugin = ''

		plugins = []
		for id,ok,msg,module in load_plugins(os.path.dirname(os.path.dirname(__file__)), 'mesmer', args=args ):
			if ok: plugins.append(module)
	
		targets		= load_targets( args, plugins )
		components	= load_components( args, plugins, targets )

		if(None in components):
			return 0

		tmp = scipy.recfromtxt( args.spec, dtype=str, unpack=True )
		n = len(tmp[0])
		spec = [ list(tmp[0]), list(tmp[1]) ]

		# make sure all the specified components are available, and get their weighting
		for i in range(n):
			if( not spec[0][i] in components.keys() ):
				return 1,"The specification component %s was not found in the provided components" % spec[0][i]
			spec[1][i] = float(spec[1][i])

		e = mesEnsemble( plugins, targets, n )
		e.component_names = spec[0]
		o = e.get_fitness(components, plugins, targets[0], spec[1])

		print "Fits to provided target data:"
		for k in o:
			print "\t%s : %.3f" % (k,o[k])

		print_plugin_state( args, 0, plugins, targets, [e])
		unload_plugins( plugins )