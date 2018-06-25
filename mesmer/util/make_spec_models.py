import os
import scipy
import shutil

from mesmer.lib.utility_objects import MESMERUtility

class MakeSpecModels(MESMERUtility):
	def __init__(self):
		super(MakeSpecModels, self).__init__()
		
		self.parser.add_argument('-spec',	required=True, 			metavar='<SPEC>',	help='Synthetic target specification file')
		self.parser.add_argument('-pdbs',	required=True,			metavar='<DIR>',	help='Directory containing named PDBs')
		self.parser.add_argument('-n',		type=int,	default=10,	metavar='N',		help='Number of most heavily weighted models to include')
		self.parser.add_argument('-out',	default='spec_models.pdb', metavar='<PDB/DIR>',	help='The name of the PDB to write the models to. Alternatively, specify a folder to copy the PDBs into')

	def run(self,args):
		tmp = scipy.genfromtxt( args.spec, usecols=(0,1), dtype=str, unpack=True )
		pdb_names	= list(tmp[0])
		pdb_weights	= map(float,tmp[1])

		# sort pdbs by their weights
		o = scipy.argsort( pdb_weights )
		pdb_names = list(scipy.take(pdb_names,o))
		pdb_names.reverse()

		if( not os.path.isdir(args.out) ):
			f = open( args.out, 'w' )

		for i in range(args.n):
			pdb = "%s%s%s.pdb" % (args.pdbs,os.sep,pdb_names[i])
			if( not os.path.exists(pdb) ):
				return 1,"ERROR:\tPDB \"%s\" not found in \"%s\"." % (pdb,args.pdbs)

			if( os.path.isdir(args.out) ):
				shutil.copy( pdb, args.out )
			else:
				f.write("MODEL        %d\n%s\nENDMDL\n" % (i+1, open(pdb, 'r').read().strip()) )

		if( not os.path.isdir(args.out) ):
			f.close()