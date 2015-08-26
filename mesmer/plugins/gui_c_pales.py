import os
import shlex
import shutil
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

		simulation = self.parser.add_argument_group("Simulation Parameters")
		simulation.add_argument('-wv',		metavar="LC Conc.",		type=float,	default=0.05,	help="Liquid crystal concentration (mg/mL)")
		simulation.add_argument('-lcS',		metavar="LC Order",		type=float,	default=0.90,	help="Liquid crystal order (0-1)")
		simulation.add_argument('-surf',	action="store_true",				default=True,	help="Select surface accessible atoms")
		simulation.add_argument('-nosurf',	action="store_true",				default=False,	help="Don't select surface accessible atoms")
		simulation.add_argument('-rA',		metavar="Atom radius",	type=float, default=0.00,	help="Atom radius, in angstroms")

		self.parser.add_argument('-Electrostatics',	default=False,	action='store_true',	help='Use electrostatic model')
		electro = self.parser.add_argument_group("Electrostatic Parameters")
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

		# option processing
		self.extra_args = shlex.split(self.options['extra']['value'])
		del self.options['extra']

		if self.options['Model']['value'] == 'Wall':
			self.extra_args.append('-bic')
		else:
			self.extra_args.append('-pf1')
		del self.options['Model']

		if self.options['Electrostatics']['value']:
			self.extra_args.append('-elPales')
		else: # remove electrostatic parameters
			self.extra_args.append('-stPales')
			for k,o in self.options.iteritems():
				if o['group'] == 'Electrostatic Parameters':
					del self.options[k] 
		del self.options['Electrostatics']

		self.template = self.options['template']['value']
		del self.options['template']
				
		return True
		
	def close(self, abort):
		return True
		
	def calculate(self, pdb, repeat=0):
		name = os.path.splitext( os.path.basename(pdb) )[0]

		if not os.path.exists(pdb):
			return False,(pdb,"Could not read file.")

		cmd = [self.path,'-pdb',pdb,'-inD',self.template,'-outD',"%s.out"%name]
		cmd.extend( self.extra_args )
		cmd.extend( makeListFromOptions(self.options) )
		print 'PALES arguments #1/2: %s'%(' '.join(cmd))

		try:
			sub = subprocess.Popen(cmd,cwd=self.outputdir)
			sub.wait()
		except Exception as e:
			return False,(pdb,"Error calling \"pales\": %s"%e)

		cmd = [self.path,'-conv','-cyana','-inD',"%s.out"%name,'-outD',"%s.tbl"%name]
		print 'PALES arguments #2/2: %s'%(' '.join(cmd))

		try:
			sub = subprocess.Popen(cmd,cwd=self.outputdir)
			sub.wait()
		except Exception as e:
			return False,(pdb,"Error calling \"pales\": %s"%e)
					
		return True,(pdb,None)
