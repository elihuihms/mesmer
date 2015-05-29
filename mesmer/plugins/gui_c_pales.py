import os
import argparse
import shutil
import shelve

from subprocess				import Popen,PIPE
from tkFileDialog			import askopenfilename

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'RDC - PALES'
		self.version = '2014.12.21'
		self.info = 'This plugin uses the external program PALES (see http://www3.mpibpc.mpg.de/groups/zweckstetter/_links/software_pales.htm) to predict residual dipolar couplings from a PDB. PALES arguments and descroptions are (C) Markus Zweckstetter.'
		self.type = 'TABL'
		self.path = 'pales'
		self.respawn = 100

		self.plugindir = os.path.dirname(os.path.realpath(__file__))
		d = shelve.open( os.path.join( self.plugindir, "gui_c_pales") )
		if not d.has_key('wv'):		d['wv']		= 0.05
		if not d.has_key('mwLC'):	d['mwLC']	= 268E3
		if not d.has_key('massLC'):	d['massLC']	= 0.05
		if not d.has_key('unitLC'):	d['unitLC']	= 1
		if not d.has_key('polyLC'):	d['polyLC']	= 1707
		if not d.has_key('lcS'):	d['lcS']	= 0.8
		if not d.has_key('pH'):		d['pH']		= 7.0
		if not d.has_key('nacl'):	d['nacl']	= 0.2
		if not d.has_key('chSurf'):	d['chSurf']	= -0.47
		if not d.has_key('maxPot'):	d['maxPot']	= 5.0
		if not d.has_key('temp'):	d['temp']	= 298.15
		if not d.has_key('bic'):	d['bic']	= False
		if not d.has_key('pf1'):	d['pf1']	= True
		if not d.has_key('surf'):	d['surf']	= True
		if not d.has_key('nosurf'):	d['nosurf']	= False
		if not d.has_key('kEne'):	d['kEne']	= 1
		if not d.has_key('kPot'):	d['kPot']	= 1
		if not d.has_key('kMono'):	d['kMono']	= 1
		if not d.has_key('kDipo'):	d['kDipo']	= 1
		if not d.has_key('kQuad'):	d['kQuad']	= 1
		if not d.has_key('extra'):	d['extra']	= ''
		
		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-bic',	default=d['bic'],	action='store_true',		help='Use wall (bicell) model')
		self.parser.add_argument('-pf1',	default=d['pf1'],	action='store_true',		help='Use rod (phage) model')
		self.parser.add_argument('-surf',	default=d['surf'],	action='store_true',		help='Select surface residues')
		self.parser.add_argument('-nosurf',	default=d['nosurf'],	action='store_true',		help='Don\'t select surface residues')
		self.parser.add_argument('-wv',		type=float,	default=d['wv'],	help='Liquid crystal concentration (mg/mL)')
		self.parser.add_argument('-mwLC',	type=float,	default=d['mwLC'],	help='Liquid crystal molecular weight (g/mol)')
		self.parser.add_argument('-massLC',	type=float,	default=d['massLC'],	help='Liquid crystal mass (g)')
		self.parser.add_argument('-unitLC',	type=float,	default=d['unitLC'],	help='Liquid crystal unit height (Angstrom)')
		self.parser.add_argument('-polyLC',	type=float,	default=d['polyLC'],	help='Liquid crystal polymerization degree')
		self.parser.add_argument('-lcS',	type=float,	default=d['lcS'],		help='Liquid crystal order (0-1)')
		self.parser.add_argument('-pH',		type=float,	default=d['pH'],	help='pH of NMRsample')
		self.parser.add_argument('-nacl',	type=float,	default=d['nacl'],	help='NaCl concentration (M)')
		self.parser.add_argument('-chSurf',	type=float,	default=d['chSurf'],	help='Surface charge density (e/nm2)')
		self.parser.add_argument('-maxPot',	type=float,	default=d['maxPot'],	help='Maximum (+/-) used potential (kT/e)')
		self.parser.add_argument('-kEne',	type=float,	default=d['kEne'],		help='Scaling of energy')
		self.parser.add_argument('-kPot',	type=float,	default=d['kPot'],		help='Scaling of potential')
		self.parser.add_argument('-kMono',	type=float,	default=d['kMono'],		help='Scaling of monopole charges')
		self.parser.add_argument('-kDipo',	type=float,	default=d['kDipo'],		help='Scaling of dipole charges')
		self.parser.add_argument('-kQuad',	type=float,	default=d['kQuad'],		help='Scaling of quadrupole charges')
		self.parser.add_argument('-temp',	type=float,	default=d['temp'],	help='Boltzmann temperature')
		self.parser.add_argument('-extra',	type=str,	default=d['extra'],		help='Additional arguments to PALES')

		d.close()

	def setup(self, pdbs, dir, options, threads):
		self.pdbs	= pdbs
		self.dir	= dir
		self.options	= options
		self.threads	= threads
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''
		
		self.options_extra = self.options['extra']['value'].split()
		del self.options['extra']
		
		self.template = askopenfilename(title='Select experimental RDC table template in PALES format:')
		if(self.template == ''):
			raise Exception( "Must select an experimental RDC table" )
		if not os.access(self.template, os.R_OK):
			raise Exception( "Could not read specified RDC table")
		
		d = shelve.open( os.path.join( self.plugindir, "gui_c_pales") )
		for arg in options:
			d[ arg ] = options[ arg ]['value']
		d.close()

	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]

		if not os.path.exists(pdb):
			raise Exception( "Could not find \"%s\"" % (pdb) )

		cmd = [self.path]
		cmd.extend( makeStringFromOptions(self.options).split() )
		cmd.extend( self.options_extra )
		cmd.extend( ['-pdb',pdb,'-inD',self.template,'-outD',"%s.out"%name] )

		try:
			pipe = Popen(cmd, cwd=self.dir, stdout=PIPE)
			pipe.wait()
		except OSError as e:
			if(e.errno == os.errno.ENOENT):
				raise Exception("Could not find \"pales\" program. Perhaps it isn't installed, or the path to it is wrong?")
			else:
				raise e
												
		cmd = [os.path.join(self.plugindir,'pales')]
		cmd.extend( ['-conv','-inD',"%s.out"%name,'-outD',"%s.rdc"%name,'-cyana'] )
		
		try:
			pipe = Popen(cmd, cwd=self.dir, stdout=PIPE)
			pipe.wait()
		except OSError as e:
			if(e.errno == os.errno.ENOENT):
				raise Exception("Could not find \"pales\" program. Perhaps it isn't installed?")
			else:
				raise e

		self.state -=1
		self.counter +=1
		return self.counter
