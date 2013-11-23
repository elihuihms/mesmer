import os
import argparse
import shutil
import sys

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

sys.path.append( os.path.dirname(__file__) )
from gui_c_deer_lib			import *

class plugin(guiCalcPlugin):

	def __init__(self, mesmerDir):
		self.name = 'DEER'
		self.version = '2013.10.18'
		self.type = 'DEER'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Dip', 	type=float, default=52.04,	required=True,	help='Dipolar susceptibility (MHz/nm^3)')
		self.parser.add_argument('-T',  	type=float, default=2.5,	required=True,	help='Final t (us)')
		self.parser.add_argument('-Tstep', 	type=float, default=0.025,	required=True,	help='Time resolution (us)')
		self.parser.add_argument('-chainAID',			default=None,	required=False,	help='Chain ID for first labeled residue')
		self.parser.add_argument('-resANum',			default='',		required=True,	help='Residue number for first labeled residue')
		self.parser.add_argument('-atomA',				default='CA',	required=True,	help='Atom name to use as center of first label distribution')
		self.parser.add_argument('-chainBID',			default=None,	required=False,	help='Chain ID for second labeled residue')
		self.parser.add_argument('-resBNum',			default='',		required=True,	help='Residue number for second labeled residue')
		self.parser.add_argument('-atomB',				default='CA',	required=True,	help='Atom name to use as center of second label distribution')
		self.parser.add_argument('-distW',	type=float,	default=5.0,	required=True,	help='Width of label distribution (angstrom)')

	def setup(self, pdbs, dir, options):
		self.pdbs	= pdbs
		self.dir	= dir
		self.args	= self.parser.parse_args( makeStringFromOptions(options).split() )
		# convert dipolar coupling to MHz/A**3
		self.args.Dip = self.args.Dip*1000.0
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

	def calculator(self):
		if(self.state != 0):	#semaphore to check if we're still busy processing
			return
		self.state = 1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		if not os.access(pdb, os.R_OK):
			raise Exception( "Could not read \"%s\"" % (pdb) )

		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]
		out = "%s%s%s.dat" % (self.dir,os.sep,name)

		# obtain distance between the two labeled residues
		distance = PDBTools.get_distance(
			pdb,
			self.args.chainAID,
			self.args.resANum,
			self.args.atomA,
			self.args.chainBID,
			self.args.resBNum,
			self.args.atomB
			)

		# generate a distance distribution
		distribution = PDBTools.make_distribution( distance, self.args.distW )

		# obtain the maximum to normalize against
		norm = DEERSim.DEER_Vt( self.args.Dip, distribution, 0.0 )

		# write normalized values to file
		f = open( out, 'w')
		for i in range( int( self.args.T / self.args.Tstep ) +1 ):
			v = DEERSim.DEER_Vt( self.args.Dip, distribution, self.args.Tstep * i )
			f.write( "%.3f\t%.5f\n" % (i*self.args.Tstep,v/norm) )
		f.close()

		self.state = 0
		self.counter +=1
		return self.counter
