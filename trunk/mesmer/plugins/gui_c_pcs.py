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

def get_atom_coords(file,chainID=None,resNum=None,atomName='CA'):

	f = open(file, 'r')

	ret = []

	line = f.readline()
	while( line ):

		if (line[0:4] != 'ATOM') and (line[0:6] != 'HETATM'):
			line = f.readline()
			continue

		if (line[21]==chainID) or (chainID==None):
			if (int(line[22:26])==int(resNum)) or (resNum==None):
				if( line[12:16].strip() == atomName ):
					ret.append( (float(line[30:38]),float(line[38:46]),float(line[46:54])) )

		line = f.readline()
	f.close()

	return ret

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'PCS - pyParaTools'
		self.version = '2013.10.18'
		self.type = 'TABL'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-chainID',			help='Chain ID for paramagnetic center')
		self.parser.add_argument('-resNum',				help='Residue number of paramagnetic center')
		self.parser.add_argument('-atom',				help='Paramagnetic center atom name')
		self.parser.add_argument('-Dax',	type=float,	help='Axial component of paramagnetic tensor',				required=True)
		self.parser.add_argument('-Drh',	type=float,	help='Rhomboidal component of paramagnetic tensor',		required=True)
		self.parser.add_argument('-Alpha',	type=float,	help='Alpha component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Beta',	type=float,	help='Beta component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Gamma',	type=float,	help='Gamma component of alignment tensor Euler angle',	required=True)

	def setup(self, pdbs, dir, options, threads):
		self.pdbs	= pdbs
		self.dir	= dir
		self.args	= self.parser.parse_args( makeStringFromOptions(options).split() )
		self.threads	= threads
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

		self.template = askopenfilename(title='Select experimental PCS table template in CYANA format:')
		if(self.template == ''):
			raise Exception( "Must select an experimental PCS table" )
		if not os.access(self.template, os.R_OK):
			raise Exception( "Could not read specified PCS table")

	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]

		if not os.access(pdb, os.R_OK):
			raise Exception( "Could not read \"%s\"" % (pdb) )

		coords = get_atom_coords( pdb, self.args.chainID, self.args.resNum, self.args.atom )

		if len(coords) < 1:
			raise Exception('Error',"Could not find a paramagnetic center using \"%s\":%i:%s" % (self.args.chainID,self.args.resNum,self.args.atom) )
		if len(coords) > 1:
			raise Exception('Error',"%i potential paramagnetic centers found using \"%s\":%i:%s" % (len(coords),self.args.chainID,self.args.resNum,self.args.atom) )

		config = [
			'',
			'pcs',
			pdb,
			self.template,
			coords[0][0],
			coords[0][1],
			coords[0][2],
			self.args.Dax,
			self.args.Drh,
			self.args.Alpha,
			self.args.Beta,
			self.args.Gamma
			]

		pcs = PCSParser( config )
		pcs.doParse()

		calc = CalcPara()
		calc.PCS(pcs, 'ZYZ')

		analysis = ExplorePara()
		analysis.buildNumbatTBL(pcs, "%s%s%s.pcs" % (self.dir,os.sep,name))

		self.state -=1
		self.counter +=1
		return self.counter
