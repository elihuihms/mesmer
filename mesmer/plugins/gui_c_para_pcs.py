import os
import sys
import argparse
import tkFileDialog
import Bio.PDB

from lib.exceptions			import *
from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

from	pyParaTools.ParaParser	import PCSParser
from	pyParaTools.CalcPara	import CalcPara
from	pyParaTools.ExplorePara	import ExplorePara

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'PCS - pyParaTools'
		self.version = '2015.06.23'
		self.info = 'This plugin uses PyParaTools (see http://comp-bio.anu.edu.au/mscook/PPT/) to calculate pseudocontact shifts from a paramagnetic atom in a PDB.'
		self.type = 'TABL'

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-chainID',			help='Chain ID for paramagnetic center')
		self.parser.add_argument('-resNum',	type=int,	help='Residue number of paramagnetic center')
		self.parser.add_argument('-atom',				help='Paramagnetic center atom name')
		self.parser.add_argument('-Dax',	type=float,	help='Axial component of paramagnetic tensor',			required=True)
		self.parser.add_argument('-Drh',	type=float,	help='Rhomboidal component of paramagnetic tensor',		required=True)
		self.parser.add_argument('-Alpha',	type=float,	help='Alpha component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Beta',	type=float,	help='Beta component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Gamma',	type=float,	help='Gamma component of alignment tensor Euler angle',	required=True)

	def setup(self, parent, options, outputpath):
		self.outputpath	= outputpath
		self.args		= self.parser.parse_args( makeStringFromOptions(options).split() )

		self.template = tkFileDialog.askopenfilename(title='Select experimental PCS table template in CYANA format:',parent=parent)
		if(self.template == ''):
			return False
		if not os.access(self.template, os.R_OK):
			raise mesPluginError("Could not read specified PCS table")
		return True

	def calculate(self, pdb):
		base = os.path.basename(pdb)
		name = os.path.splitext(base)[0]
		try:
			parser	= Bio.PDB.PDBParser(QUIET=True)
			model	= parser.get_structure('',pdb)[0]
		except Exception as e:
			return True,(pdb,"Could not parse PDB file: %s"%(e))

		try:
			coord	= model[ self.args.chainID ][ int(self.args.resNum) ][ self.args.atom ].get_coord()
		except (IndexError,KeyError):
			return True,(pdb,"Could not find specified atom in PDB.") 

		config = [
			'',
			'pcs',
			pdb,
			self.template,
			coord[0],
			coord[1],
			coord[2],
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
		analysis.buildNumbatTBL(pcs, "%s.pcs" % (os.path.join(self.outputpath,name)))
		
		return False,(pdb,None)