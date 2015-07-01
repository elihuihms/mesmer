import os
import argparse
import tkFileDialog
import Bio.PDB

from lib.exceptions			import *
from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

from	pyParaTools.ParaParser	import *
from	pyParaTools.CalcPara	import *
from	pyParaTools.ExplorePara	import *

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'RDC - pyParaTools'
		self.version = '2015.06.23'
		self.info = 'This plugin uses PyParaTools (see http://comp-bio.anu.edu.au/mscook/PPT/) to calculate paragmagnetic residual dipolar couplings resulting from a paramagnetic atom in a PDB.'
		self.type = 'TABL'

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Dax',	type=float,	help='Axial component of diffusion tensor',				required=True)
		self.parser.add_argument('-Drh',	type=float,	help='Rhomboidal component of diffusion tensor',		required=True)
		self.parser.add_argument('-Alpha',	type=float,	help='Alpha component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Beta',	type=float,	help='Beta component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-Gamma',	type=float,	help='Gamma component of alignment tensor Euler angle',	required=True)
		self.parser.add_argument('-B0',		type=float,	help='Field strength (Gauss)',	default=16.44)
		self.parser.add_argument('-temp',	metavar='Temperature',	type=float,	help='Temperature (K)',			default=298.0)

	def setup(self, parent, options, outputpath):
		self.outputpath	= outputpath
		self.args		= self.parser.parse_args( makeStringFromOptions(options).split() )

		self.template = tkFileDialog.askopenfilename(message='Select experimental RDC table template in CYANA format:',parent=parent)
		if(self.template == ''):
			return False
		if not os.access(self.template, os.R_OK):
			raise mesPluginError("Could not read specified RDC table")
		return True

	def calculate(self, pdb):
		base = os.path.basename(pdb)
		name = os.path.splitext(base)[0]

		if not os.access(pdb, os.R_OK):
			return True,(pdb,"Failure reading.")

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
		analysis.buildNumbatTBL(rdc, "%s.rdc" % (os.path.join(self.outputpath,name)))

		return False,(pdb,None)
