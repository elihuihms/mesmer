import os
import tarfile

from lib.utility_objects import MESMERUtility

class MakeModels(MESMERUtility):
	def __init__(self):
		super(MakeModels, self).__init__()

		group1 = self.parser.add_argument_group('Input options')
		group1.add_argument('pdbs',		nargs='+',				default=[],		metavar='DIR',							help='Directory(s) containing named PDBs')
		group1.add_argument('-names',	nargs='*',				default=[],		metavar='NAME',							help='Extract named PDBs')

		group2 = self.parser.add_argument_group('PDBs from ensemble file')
		group2.add_argument('-ensembles',						default=None,	metavar='ensembles_*.tbl',				help='MESMER ensemble state file')
		group2.add_argument('-id',		type=int,				default=0,		metavar='N',							help='Save components from the ensemble IDs provided by get_ensemble_stats')
		group2.add_argument('-best',	action='store_true',	default=False,											help='Save only the best ensemble components')

		group3 = self.parser.add_argument_group('PDBs from statistics file')
		group3.add_argument('-stats',							default=None,	metavar='component_statistics_*.tbl',	help='MESMER component statistics file')
		group3.add_argument('-Pmin',	type=float,				default=5,		metavar='5%',							help='Minimum prevalence for components to be included')
		group3.add_argument('-Wmin',	type=float,				default=0.05,	metavar='0.05',							help='Minimum weighting for components to be included')

		group4 = self.parser.add_argument_group('Output options')
		group4.add_argument('-out',								required=True,	metavar='*.pdb',						help='Filename to save output PDB under')
		group4.add_argument('-wAttr',	action='store_true',	default=False,											help='Write UCSF Chimera attribute files for prevalence and weighting of each component')
		group4.add_argument('-wPyMol',	action='store_true',	default=False,											help='Write PyMol scripts for prevalence and weighting of each component')

	def run(self,args):
		if( len(args.pdbs) == 0 ):
			return 1,"ERROR:\tMust specify at least one directory or tarball containing PDBs."

		for tmp in args.pdbs:
			if( os.path.isfile(tmp) ):
				if( not tarfile.is_tarfile(tmp) ):
					return 1,"ERROR:\t-pdb option \"%s\" file is not readable." % (tmp)
			elif( not os.path.isdir(tmp) ):
				return 1,"ERROR:\t-pdb option \"%s\" does not exist." % (tmp)

		# open tarballs and PDB dirs
		dirs, tarballs = [], []
		for tmp in args.pdbs:
			if( os.path.isfile(tmp) ):
				try:
					tarballs.append( tarfile.open( tmp, 'r:*') )
				except Exception as e:
					return 1,"ERROR:\tFailure opening tar files. Reason: %s" % (e)
			else:
				dirs.append( tmp )

		names, prevalences, weights = [], [], []
		if( len(args.names) > 0 ):
			for n in args.names:
				names.append( n )
				prevalences.append( 1.0 )
				weights.append( 1.0 )

		elif( args.ensembles ):
			try:
				ensemble_stats = get_ensembles_from_state( args.ensembles, unique=True )
			except Exception as e:
				return 1,"ERROR:\tCould not load ensemble information from state file. Reason: %s" % (e)

			if( args.best ):
				tmp = ensemble_stats[0]['components']
			else:
				tmp = ensemble_stats[args.id]['components']

			for (i,n) in enumerate( tmp ):
				names.append( n )
				prevalences.append( 1.0 )
				weights.append( ensemble_stats[args.id]['weights'][i] )

		elif( args.stats ):
			try:
				f = open( args.stats, 'r' )
				lines = f.readlines()[1:] # drop the header
				f.close()
			except Exception as e:
				return 1,"ERROR:\tCould not read -input option \"%s\": %s" % (args.stats,e)

			for l in lines:
				fields = l.strip().split()

				if(len(fields)<4):
					continue

				if( float(fields[1]) < args.Pmin ):
					continue
				if( float(fields[3]) < args.Wmin ):
					continue

				print "\t%s\t%s\t%s" % (fields[0],fields[1],fields[3])

				names.append( fields[0] )
				prevalences.append( float(fields[1]) )
				weights.append( float(fields[3]) )
		else:
			return 1,"ERROR:\tMust provide a component name, ensemble state or component statistics file."

		if(len(names)==0):
			return 0,"WARNING:\tNo components found."

		try:
			write_named_pdbs( args.out, names, dirs, tarballs )
		except ModelExtractionException as e:
			return 1,"ERROR:\t%s" % (e.msg)

		if( args.wAttr ):
			try:
				name = "%s_prevalence" % os.path.splitext(os.path.basename(args.out))[0]
				path = "%s_prevalence.attr" % os.path.splitext(args.out)[0]
				write_model_attributes( path, name, prevalences )

				name = "%s_weights" % os.path.splitext(os.path.basename(args.out))[0]
				path = "%s_weights.attr" % os.path.splitext(args.out)[0]
				write_model_attributes( path, name, [100*w for w in weights] )
			except Exception as e:
				return 1,"ERROR:\tCould not write attribute lists: %s" % (e)

		if( args.wPyMol ):
			try:
				name = "%s_prev" % os.path.splitext(os.path.basename(args.out))[0]
				path = "%s_prev.py" % os.path.splitext(args.out)[0]
				write_model_script( path, name, [p/100.0 for p in prevalences] )

				name = "%s_weights" % os.path.splitext(os.path.basename(args.out))[0]
				path = "%s_weights.py" % os.path.splitext(args.out)[0]
				write_model_script( path, name, weights )
			except Exception as e:
				return 1,"ERROR:\tCould not write coloration script: %s" % (e)
				
		return 0