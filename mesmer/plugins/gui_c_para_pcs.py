import os
import argparse
import tkFileDialog
import Bio.PDB

from mesmer.lib.exceptions			import *
from mesmer.lib.gui.plugin_objects	import guiCalcPlugin
from mesmer.lib.gui.tools_plugin	import makeListFromOptions

from	pyParaTools.ParaParser	import PCSParser
from	pyParaTools.CalcPara	import CalcPara
from	pyParaTools.ExplorePara	import ExplorePara

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'PCS - pyParaTools'
		self.version = '1.0.0'
		self.info = 'This plugin uses PyParaTools (see http://comp-bio.anu.edu.au/mscook/PPT/) to calculate pseudocontact shifts from a paramagnetic atom in a PDB.'
		self.types = ('TABL',)

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-chainID',			help='Chain ID for paramagnetic center')
		self.parser.add_argument('-resNum',	type=int,	help='Residue number of paramagnetic center')
		self.parser.add_argument('-atom',				help='Paramagnetic center atom name')
		self.parser.add_argument('-Dax',	type=float,	help='Axial component of paramagnetic tensor',			required=True)
		self.parser.add_argument('-Drh',	type=float,	help='Rhomboidal component of paramagnetic tensor',		required=True)
		self.parser.add_argument('-Alpha',	type=float,	help='Alpha component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Beta',	type=float,	help='Beta component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Gamma',	type=float,	help='Gamma component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-template', default='template.pcs', metavar='FILE', help="Experimental PCS data template, in CYANA format", required=True)

	def setup(self, parent, options, outputpath):
		self.outputpath	= outputpath
		self.args		= self.parser.parse_args( makeListFromOptions(options) )

		if not os.access(self.args.template, os.R_OK):
			raise mesPluginError("Could not read specified PCS table")
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
			coord	= model[ self.args.chainID ][ int(self.args.resNum) ][ self.args.atom ].get_coord()
		except (IndexError,KeyError):
			return False,(pdb,"Could not find specified atom in PDB.") 

		config = [
			'',
			'pcs',
			pdb,
			self.args.template,
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
		
		return True,(pdb,None)