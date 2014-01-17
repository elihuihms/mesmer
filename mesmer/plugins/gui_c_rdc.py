import os
import argparse
import shutil
import sys

from tkFileDialog			import askopenfilename

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

# preflight Bio.PDB and numpy before importing pyParaTools
try:
	import Bio.PDB
except:
	raise Exception("Failed to import BioPython")
try:
	import numpy
except:
	raise Exception("Failed to import Numpy")

from	pyParaTools.ParaParser	import *
from	pyParaTools.CalcPara	import *
from	pyParaTools.ExplorePara	import *

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'RDC - pyParaTools'
		self.version = '2013.10.18'
		self.type = 'TABL'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Dax',	type=float,	help='Axial component of diffusion tensor',				required=True)
		self.parser.add_argument('-Drh',	type=float,	help='Rhomboidal component of diffusion tensor',		required=True)
		self.parser.add_argument('-Alpha',	type=float,	help='Alpha component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Beta',	type=float,	help='Beta component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Gamma',	type=float,	help='Gamma component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-B0',		type=float,	help='Field strength (Gauss)',	default=16.44)
		self.parser.add_argument('-temp',	type=float,	help='Temperature (K)',			default=298.0)

	def setup(self, pdbs, dir, options, threads):
		self.pdbs	= pdbs
		self.dir	= dir
		self.args	= self.parser.parse_args( makeStringFromOptions(options).split() )
		self.threads	= threads
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

		self.template = askopenfilename(title='Select experimental RDC table template in CYANA format:')
		if(self.template == ''):
			raise Exception( "Must select an experimental RDC table" )
		if not os.access(self.template, os.R_OK):
			raise Exception( "Could not read specified RDC table")

	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]

		if not os.access(pdb, os.R_OK):
			raise Exception( "Could not read \"%s\"" % (pdb) )

		config = [
			'',
			'rdc',
			pdb,
			self.template,
			self.args.Dax,
			self.args.Drh,
			self.args.Alpha,
			self.args.Beta,
			self.args.Gamma,
			self.args.B0,
			self.args.temp,
			1.0
			]

		rdc = RDCParser( config )
		rdc.doParse()

		calc = CalcPara()
		calc.RDC(rdc, 'ZYZ')

		analysis = ExplorePara()
		analysis.buildNumbatTBL(rdc, "%s%s%s.rdc" % (self.dir,os.sep,name))

		self.state -=1
		self.counter +=1
		return self.counter
