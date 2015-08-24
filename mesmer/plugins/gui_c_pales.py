import os
import glob
import shlex
import argparse
import subprocess
import tempfile

from threading import Timer

from lib.exceptions			import *
from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeListFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'RDC - PALES'
		self.version = '0.9.0'
		self.info = 'This plugin uses the external program PALES (see http://www3.mpibpc.mpg.de/groups/zweckstetter/_links/software_pales.htm) to predict residual dipolar couplings from a PDB. PALES arguments and descroptions are (C) Markus Zweckstetter.'
		self.types = ('TABL',)
		self.path = 'pales'

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-Model',	default='Wall',	choices=['Wall','Rod'],	help='Steric model, i.e. Bicelles (wall), Phage (rod)')
		self.parser.add_argument('-template', metavar='FILE', help="Experimental RDC data template, in CYANA format", required=True)

		simulation = self.parser.add_argument_group("Simulation Parameters:")
		simulation.add_argument('-wv',		metavar="LC Conc.",		type=float,	default=0.05,	help="Liquid crystal concentration (mg/mL)")
		simulation.add_argument('-lcS',		metavar="LC Order",		type=float,	default=0.90,	help="Liquid crystal order (0-1)")
		simulation.add_argument('-surf',	action="store_true",				default=True,	help="Select surface accessible atoms")
		simulation.add_argument('-nosurf',	action="store_true",				default=False,	help="Don't select surface accessible atoms")
		simulation.add_argument('-rA',		metavar="Atom radius",	type=float, default=0.00,	help="Atom radius, in angstroms")

		self.parser.add_argument('-Electrostatics',	default=False,	action='store_true',	help='Use electrostatic model')
		electro = self.parser.add_argument_group("Electrostatic Parameters:")
		electro.add_argument('-mwLC',	type=float,	default=268E3,			help='Liquid crystal molecular weight (g/mol)')
		electro.add_argument('-massLC',	type=float,	default=0.05,			help='Liquid crystal mass (g)')
		electro.add_argument('-unitLC',	type=float,	default=1.00,			help='Liquid crystal unit height (Angstrom)')
		electro.add_argument('-polyLC',	type=float,	default=1707,			help='Liquid crystal polymerization degree')
		electro.add_argument('-pH',		type=float,	default=7.00,			help='pH of NMRsample')
		electro.add_argument('-nacl',	type=float,	default=0.2,			help='NaCl concentration (M)', metavar='NaCl')
		electro.add_argument('-chSurf',	type=float,	default=-0.47,			help='Surface charge density (e/nm2)')
		electro.add_argument('-maxPot',	type=float,	default=5.00,			help='Maximum (+/-) used potential (kT/e)')
		electro.add_argument('-temp',	type=float,	default=298.15,			help='Boltzmann temperature')

		self.parser.add_argument('-extra',			default='',				help='Additional arguments to PALES', metavar="Extra args")
				
	def setup(self, parent, options, outputdir):
		self.options	= options
		self.outputdir	= outputdir

		def getopt(list,name):
			for i,o in enumerate(list):
				if o['name'] == name:
					return i,o

		# option processing
		self.extra_options = shlex.split(getopt(self.options,'extra')[1]['value'])
		del self.options[getopt(self.options,'value')[0]]

		if getopt(self.options,'Model')[1]['value'] == 'Wall':
			self.extra_options.append('-bic')
		else:
			self.extra_options.append('-pf1')
		del self.options[getopt(self.options,'Model')[0]]

		if getopt(self.options,'Electrostatics')[1]['value']:
			self.extra_options.append('-elPales')
		else:
			self.extra_options.append('-stPales')

		del self.options[getopt(self.options,'Electrostatics')[0]]

		self.template = getopt(self.options,'template')[1]['value']
		del self.options[getopt(self.options,'template')[0]]
		
		# check that pales is installed
		try:
			sub = subprocess.Popen([self.path], stdout=subprocess.PIPE)
			output,err = sub.communicate()
			code = sub.wait()
		except Exception as e:
			if(e.errno == os.errno.ENOENT):
				raise mesPluginError("Could not find \"pales\" excecutable, is it installed?")
			else:
				raise e
				
		print "PALES arguments: ",
		cmd = [self.path,'-pdb','<input.pdb>','-inD',self.template,'-outD','<output.tbl>']
		cmd.extend( makeListFromOptions(self.options) )
		cmd.extend( self.extra_options )
				
		return True
		
	def close(self, abort):
		return True
		
	def calculate(self, pdb, repeat=0):
		base = os.path.basename(pdb)
		name = os.path.splitext( base )[0]
		tabl = os.path.join(self.outputdir,"%s.tbl"%name)

		if not os.path.exists(pdb):
			return False,(pdb,"Could not read file.")

		cmd = [self.path,'-pdb',pdb,'-inD',self.template,'-outD',tabl]
		cmd.extend( makeListFromOptions(self.options) )
		cmd.extend( self.extra_options )
		
		try:
			sub = subprocess.Popen(cmd)
			sub.wait()

		except Exception as e:
			return False,(pdb,"Error calling \"pales\" program (%s): %s" %(e,err))
					
		return True,(pdb,None)
