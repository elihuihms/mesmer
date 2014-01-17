import os
import argparse
import shutil
import sys

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

from gui_c_deer_lib			import *

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'DEER'
		self.version = '2013.12.06'
		self.type = 'DEER'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Dip', 	type=float, default=52.04,	required=True,	help='Dipolar susceptibility (MHz/nm^3)')
		self.parser.add_argument('-T',  	type=float, default=2.5,	required=True,	help='Final t (us)')
		self.parser.add_argument('-Tstep', 	type=float, default=0.025,	required=True,	help='Time resolution (us)')
		self.parser.add_argument('-chainAID',			default=None,	required=False,	help='Chain ID for first labeled residue')
		self.parser.add_argument('-resANum',			default='',		required=True,	help='Residue number for first labeled residue')
		self.parser.add_argument('-chainBID',			default=None,	required=False,	help='Chain ID for second labeled residue')
		self.parser.add_argument('-resBNum',			default='',		required=True,	help='Residue number for second labeled residue')
		self.parser.add_argument('-distW',	type=float,	default=5.75,	required=True,	help='Probe isolinker distribution  width (angstrom)')
		self.parser.add_argument('-linkR',	type=float, default=4.04,	required=True,	help='Probe isolinker length (angstrom)')

	def setup(self, pdbs, dir, options, threads):
		self.pdbs	= pdbs
		self.dir	= dir
		self.args	= self.parser.parse_args( makeStringFromOptions(options).split() )
		self.threads	= threads
		# convert dipolar coupling to MHz/A**3
		self.args.Dip = self.args.Dip*1000.0
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		f = open( self.pdbs[self.counter], 'r' ) # get a handle to the coordinate file

		# obtain distance between the two labeled residues
		distance = PDBTools.get_distance(
			f,
			self.args.chainAID,
			self.args.resANum,
			'CA',
			self.args.chainBID,
			self.args.resBNum,
			'CA')

		# obtain the colinearity of the two labeled residues' CA-CB bond
		orientation = PDBTools.get_alignment(
			f,
			self.args.chainAID,
			self.args.resANum,
			'CA',
			'CB',
			self.args.chainBID,
			self.args.resBNum,
			'CA',
			'CB')

		f.close()

		# generate a distance distribution
		tmp = PDBTools.make_distribution( distance, self.args.distW )

		# modify distribution according to linker alignment
		distribution = []
		for (r,W) in tmp:
			distribution.append( (r -(orientation * self.args.linkR), W) )

		# obtain the maximum intensity for normalization
		norm = DEERSim.DEER_Vt( self.args.Dip, distribution, 0.0 )

		# write normalized values to file
		f = open( "%s%s%s.dat" % (self.dir, os.sep, os.path.basename(self.pdbs[self.counter])), 'w')
		for i in range( int( self.args.T / self.args.Tstep ) +1 ):
			v = DEERSim.DEER_Vt( self.args.Dip, distribution, self.args.Tstep * i )
			f.write( "%.3f\t%.5f\n" % (i*self.args.Tstep,v/norm) )
		f.close()

		self.state -=1
		self.counter +=1
		return self.counter
