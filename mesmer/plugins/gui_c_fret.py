import os
import argparse
import tkFileDialog

from subprocess				import Popen,PIPE

from mesmer.lib.exceptions			import *
from mesmer.lib.plugin_functions	import list_from_parser_dict
from mesmer.lib.gui.plugin_objects	import guiCalcPlugin

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'FRET'
		self.version = '1.1.0'
		self.info = 'This plugin predicts fluorescence lifetime data from a PDB containing two labeling sites.'
		self.types = ('CURV',)

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-TDi',	type=float,	help='Intrinsic donor lifetime', required=True)
		self.parser.add_argument('-R0',		type=float,	help='FRET pair Forster distance (angstroms)', required=True)
		self.parser.add_argument('-dR',		type=float,	help='FRET pair Forster distance variability', required=True)
		self.parser.add_argument('-QD',					help='Donor PDB pseudoatom name', required=True)
		self.parser.add_argument('-QA', 				help='Acceptor PDB pseudoatom name', required=True)
		self.parser.add_argument('-fA',		type=float,	help='The fraction of acceptor sites actually labeled with an acceptor dye.', default=1.0)
		self.parser.add_argument('-SkipChain', action='store_true', help='Skip acceptor fluorophores in the same chain as the donor.')
		self.parser.add_argument('-SkipModel', action='store_true', help='Skip acceptor fluorophores in the same model as the donor.')

	def setup(self, parent, options, outputpath):
		self.options	= options
		self.outputpath	= outputpath
		
		self.prog = os.path.join(os.path.dirname(__file__),'gui_c_fret_lib','pdb_fret_sim.py')
		if not os.access(self.prog, os.X_OK):
			raise mesPluginError("Could not execute pdb_fret_sim.py")

		self.irf = tkFileDialog.askopenfilename(title='Select instrument response function (IRF) file:',parent=parent)
		if(self.irf == ''):
			return False
		if not os.access(self.irf, os.R_OK):
			raise mesPluginError("Could not read specified IRF file")
		return True

	def calculate(self, pdb):
		base = os.path.basename(pdb)
		name = os.path.splitext(base)[0]
		out = "%s%s%s.dat" % (self.outputpath,os.sep,name)

		if not os.access(pdb, os.R_OK):
			return False,(pdb,"Failure reading \"%s\"."%pdb)

		cmd = [self.prog]
		cmd.extend( list_from_parser_dict(self.options) )
		cmd.extend( ['-TAi','1.0','-irf',self.irf,'-pdb',pdb,'-out',out] )
		pipe = Popen(cmd, cwd=self.outputpath, stdout=PIPE)
		pipe.wait()

		if( pipe.returncode != 0 ):
			return False(pdb,"Lifetime calculation failed: %s." % (pipe.stdout.read()) )
		if not os.access(out, os.R_OK):
			return False,(pdb,"Lifetime calculation failed: %s" % (pipe.stdout.read()) )

		return True,(pdb,None)