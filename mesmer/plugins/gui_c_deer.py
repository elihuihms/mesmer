import os
import argparse
import shutil
import sys

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeListFromOptions

from gui_c_deer_lib			import *

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'DEER'
		self.version = '0.9.0'
		self.info = 'This plugin predicts a DEER time trace from a PDB containing two spin-labeled residues.'
		self.types = ('DEER',)

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Dip', 	type=float, default=52.04,	required=True,	help='Dipolar susceptibility (MHz/nm^3)')
		self.parser.add_argument('-T',  	type=float, default=2.5,	required=True,	help='Final t (us)')
		self.parser.add_argument('-Tstep', 	type=float, default=0.025,	required=True,	help='Time resolution (us)')
		self.parser.add_argument('-chainAID',			default=None,	required=False,	help='Chain ID for first labeled residue')
		self.parser.add_argument('-resANum',			default='',		required=True,	help='Residue number for first labeled residue')
		self.parser.add_argument('-chainBID',			default=None,	required=False,	help='Chain ID for second labeled residue')
		self.parser.add_argument('-resBNum',			default='',		required=True,	help='Residue number for second labeled residue')
		self.parser.add_argument('-distW',	type=float,	default=5.75,	required=True,	help='Probe isolinker distribution  width (angstrom)')
#		self.parser.add_argument('-linkR',	type=float, default=4.04,	required=True,	help='Probe isolinker length (angstrom)')

	def setup(self, parent, options, outputdir):
		self.outputdir	= outputdir
		self.args	= self.parser.parse_args( makeListFromOptions(options) )
		self.args.Dip = self.args.Dip*1000.0 # convert dipolar coupling to MHz/A**3
		return True

	def calculate(self, pdb):
		base = os.path.basename(pdb)
		name = os.path.splitext(base)[0]
			
		try:
			parser	= Bio.PDB.PDBParser(QUIET=True)
			model	= parser.get_structure('',pdb)[0]
		except Exception as e:
			return False,(pdb,"Could not parse PDB file: %s"%(e))
			
		try:
			atomA	= model[ self.args.chainAID ][ self.args.resANum ][ 'CB' ]
		except (IndexError,KeyError):
			return False,(pdb,"Could not find a C-beta atom for residue %s:%i."%(self.args.chainAID,self.args.resANum)) 

		try:
			atomB	= model[ self.args.chainBID ][ self.args.resBNum ][ 'CB' ]
		except (IndexError,KeyError):
			return False,(pdb,"Could not find a C-beta atom for residue %s:%i."%(self.args.chainAID,self.args.resANum)) 

		# generate a distance distribution
		tmp = PDBTools.make_distribution( atomA-atomB, self.args.distW )

#		# modify distribution according to linker alignment
		distribution = []
		for (r,W) in tmp:
			distribution.append( (r -(1.0 * self.args.linkR), W) )
#			distribution.append( (r -(orientation * self.args.linkR), W) )

		# obtain the maximum intensity for normalization
		norm = DEERSim.DEER_Vt( self.args.Dip, distribution, 0.0 )

		# write normalized values to file
		f = open( "%s%s%s.dat" % (self.outputdir, os.sep, name, 'w') )
		for i in range( int( self.args.T / self.args.Tstep ) +1 ):
			v = DEERSim.DEER_Vt( self.args.Dip, distribution, self.args.Tstep * i )
			f.write( "%.3f\t%.5f\n" % (i*self.args.Tstep,v/norm) )
		f.close()

		return True,(pdb,None)