import os
import argparse
import subprocess

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'SAXS - Crysol'
		self.version = '2013.09.13'
		self.info = 'This plugin uses the external program CRYSOL (see http://www.embl-hamburg.de/biosaxs/manuals/crysol.html) to predict a SAXS profile from a PDB. CRYSOL arguments and descriptions (C) the ATSAS team.'
		self.type = 'SAXS'
		self.path = 'crysol'

		self.parser = argparse.ArgumentParser(prog=self.name)
		#self.parser.add_argument('-lm',		default='',	help='Maximum order of harmonics (default 15)')
		#self.parser.add_argument('-fb',		default='',	help='Order of fibonacci grid(default 17)')
		self.parser.add_argument('-sm',		type=float,	default=0.5,	help='Maximum scattering vector')
		self.parser.add_argument('-ns',		type=int,	default=128,	help='# points in the computed curve')
		self.parser.add_argument('-dns',	type=float,	default=0.334,	help='Solvent density (default 0.334 e/A**3)')
		self.parser.add_argument('-dro',	type=float,	default=0.03,	help='Contrast of hydration shell (default 0.03 e/A**3)')
		self.parser.add_argument('-eh',		action='store_true', 		help='Account for explicit hydrogens')

	def setup(self, parent, options, outputdir):
		self.options	= options
		self.outputdir	= outputdir
		return True

	def calculate(self, pdb):
		base = os.path.basename(pdb)
		name = os.path.splitext( base )[0]

		if not os.path.exists(pdb):
			return True,(pdb,"Could not read file.")

		cmd = [self.path]
		cmd.extend( makeStringFromOptions(self.options).split() )
		cmd.append( pdb )
				
		try:
			retcode = subprocess.call(cmd, cwd=self.outputdir)
		except OSError as e:
			if(e.errno == os.errno.ENOENT):
				return True,(pdb,"Could not find \"crysol\" program. Perhaps it isn't installed, or the path to it is wrong?")
			else:
				return True,(pdb,"Error calling \"crysol\" program: %s"%(e))

		if retcode != 0:
			return True,(pdb,"Error calling crysol. Returncode: %i"%(i))

		tmp = "%s%s%s00.int" % (self.outputdir,os.sep,name)
		if not os.path.exists(tmp):
			return True,(pdb,"Failed to calculate SAXS profile %s. CRYSOL output: %s" % (tmp,pipe.stdout.read()))

		try:
			f = open( "%s%s%s.dat" % (self.outputdir,os.sep,name), 'w' )
			for l in open( tmp ).readlines()[1:-1]:
				f.write( "%s\n" % ("\t".join( l.split()[0:2] ) ) )
			f.close()
		except:
			return True,(pdb,"Could not clean up CRYSOL profile \"%s\""%(tmp))

		try:
			os.remove("%s%s%s00.log" % (self.outputdir,os.sep,name) )
			os.remove("%s%s%s00.int" % (self.outputdir,os.sep,name) )
			os.remove("%s%s%s00.alm" % (self.outputdir,os.sep,name) )
		except:
			pass

		return False,(pdb,None)