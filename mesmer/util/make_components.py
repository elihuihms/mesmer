from mesmer.lib.utility_objects import MESMERUtility

class MakeComponents(MESMERUtility):
	def __init__(self):
		super(MakeComponents, self).__init__()
		parser.add_argument('-template',	action='store',		required=True,			metavar='FILE',		help='Component template file')
		parser.add_argument('-values',		action='store',		required=True,			metavar='FILE',		help='Component values table file')
		parser.add_argument('-data',		action='store',		default=[],	nargs='*',	metavar='DIR(s)',	help='Component data file directory')
		parser.add_argument('-out',			action='store',		default='components',	metavar='DIR',		help='Output directory name')

	def run(self,args):
		if os.path.isdir(args.out):
			print "ERROR:\tComponent output directory \"%s\" already exists." % (args.out)
			return 1

		try:
			os.mkdir(args.out)
		except OSError:
			print "ERROR:\tCouldn't create component output directory \"%s\"." % (args.out)
			return 2

		try:
			handle = open( args.template, 'r' )
		except IOError:
			print "ERROR:\tCould not open template file \"%s\"." % (args.template)
			return 3

		template = handle.read()
		handle.close()

		try:
			component_vals = get_component_values( args.values )
		except ComponentGenException as e:
			print e.msg
			return 4

		try:
			component_dirs = match_data_files( component_vals.keys(), args.data )
		except ComponentGenException as e:
			print e.msg
			return 5

		try:
			write_component_files( component_vals, component_dirs, template, args.out )
		except  ComponentGenException as e:
			print e.msg
			return 6

		return 0
