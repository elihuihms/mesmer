import os
import argparse
import shutil

from subprocess				import Popen,PIPE
from tkFileDialog			import askopenfilename

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'FRET'
		self.version = '2013.10.18'
		self.type = 'CURV'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-TDi',	type=float,	help='Intrinsic donor lifetime', required=True)
		self.parser.add_argument('-R0',		type=float,	help='FRET pair Forster distance (angstroms)', required=True)
		self.parser.add_argument('-dR',		type=float,	help='FRET pair Forster distance variability', required=True)
		self.parser.add_argument('-QD',					help='Donor PDB pseudoatom name', required=True)
		self.parser.add_argument('-QA', 				help='Acceptor PDB pseudoatom name', required=True)
		self.parser.add_argument('-fA',		type=float,	help='The fraction of acceptor sites actually labeled with an acceptor dye.', default=1.0)
		self.parser.add_argument('-SkipChain', action='store_true', help='Skip acceptor fluorophores in the same chain as the donor.')
		self.parser.add_argument('-SkipModel', action='store_true', help='Skip acceptor fluorophores in the same model as the donor.')

	def setup(self, pdbs, dir, options, threads):
		self.pdbs	= pdbs
		self.dir	= dir
		self.options	= options
		self.threads	= threads
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

		self.prog = os.path.join(os.path.dirname(__file__),'gui_c_fret_lib','pdb_fret_sim.py')
		if not os.access(self.prog, os.X_OK):
			raise Exception( "Could not execute pdb_fret_sim.py" )

		self.irf = askopenfilename(title='Select instrument response function (IRF) file:')
		if(self.irf == ''):
			raise Exception( "Must select an IRF file" )
		if not os.access(self.irf, os.R_OK):
			raise Exception( "Could not read specified IRF file")

	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]
		out = "%s%s%s.dat" % (self.dir,os.sep,name)

		if not os.access(pdb, os.R_OK):
			raise Exception( "Could not read \"%s\"" % (pdb) )

		cmd = [self.prog]
		cmd.extend( makeStringFromOptions(self.options).split() )
		cmd.extend( ['-TAi','1.0','-irf',self.irf,'-pdb',pdb,'-out',out] )
		pipe = Popen(cmd, cwd=self.dir, stdout=PIPE)
		pipe.wait()

		if( pipe.returncode != 0 ):
			raise Exception( "Lifetime calculation failed for \"%s\". %s" % (pdb,pipe.stdout.read()) )
		if not os.access(out, os.R_OK):
			raise Exception( "Lifetime calculation failed for \"%s\". %s" % (pdb,pipe.stdout.read()) )

		self.state -=1
		self.counter +=1
		return self.counter
