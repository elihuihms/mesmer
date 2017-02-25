import os
import glob
import shutil
import argparse
import subprocess
import tempfile

from threading import Timer

from lib.exceptions			import *
from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeListFromOptions

_CRYSOL_TIMER = 10000 # time to wait for crysol to finish calculating (in ms)
_CRYSOL_RETRY = 5 # crysol occasionally fails for unknown reasons, try again

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'SAXS - Crysol'
		self.version = '1.0.0'
		self.info = 'This plugin uses the external program CRYSOL (see http://www.embl-hamburg.de/biosaxs/manuals/crysol.html) to predict a SAXS profile from a PDB. CRYSOL arguments and descriptions (C) the ATSAS team.'
		self.types = ('SAXS',)
		self.path = 'crysol'

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-sm',		metavar="Maximum q",		type=float,	default=0.5,	help='Maximum scattering vector')
		self.parser.add_argument('-ns',		metavar="q Points",			type=int,	default=128,	help='# points in the computed curve')
		self.parser.add_argument('-dns',	metavar="Solvent density",	type=float,	default=0.334,	help='Solvent density (default 0.334 e/A**3)')
		self.parser.add_argument('-dro',	metavar="Shell contrast",	type=float,	default=0.03,	help='Contrast of hydration shell (default 0.03 e/A**3)')
#		self.parser.add_argument('-lm',		default='',	help='Maximum order of harmonics (default 15)')
#		self.parser.add_argument('-fb',		default='',	help='Order of fibonacci grid(default 17)')
#		self.parser.add_argument('-eh',		action='store_true', 		help='Account for explicit hydrogens')

	def setup(self, parent, options, outputdir):
		self.options	= options
		self.outputdir	= outputdir
		self.tempdir	= tempfile.mkdtemp()
		
		try:
			sub = subprocess.Popen([self.path,'-v'], stdout=subprocess.PIPE)
			output,err = sub.communicate()
			code = sub.wait()
		except Exception as e:
			if(e.errno == os.errno.ENOENT):
				raise mesPluginError("Could not find \"crysol\" excecutable, is it installed?")
			else:
				raise e
		
		# check crysol version
#		def vsplit(v):
#			return tuple(map(int,(v.split('.'))))
#				
#		crysol_version = output.strip().split()[1][1:]
#		if vsplit(crysol_version) < vsplit('2.8.0'):
#			raise mesPluginError("Installed crysol version %s is too old, MESMER requires at least version 2.8.0"%(crysol_version))
				
		return True
		
	def close(self, abort):
		shutil.rmtree( self.tempdir )
		return True
		
	def calculate(self, pdb, repeat=0):
		base = os.path.basename(pdb)
		name = os.path.splitext( base )[0]

		if not os.path.exists(pdb):
			return False,(pdb,"Could not read file.")

		cmd = [self.path]
		cmd.extend( makeListFromOptions(self.options) )
		cmd.append( pdb )
		
		try:
			sub = subprocess.Popen(cmd, cwd=self.tempdir)
			
			# timer to make sure crysol call does not hang
			kill_proc = lambda p: p.kill()
			timer = Timer(_CRYSOL_TIMER/1000, kill_proc, [sub])
			timer.start()
			sub.wait()
			timer.cancel()

		except Exception as e:
				return False,(pdb,"Error calling \"crysol\": %s" %e)
		
		# crysol sometimes fucks up and increments
		tmp = glob.glob( os.path.join(self.tempdir,"%s??.int"%name) )
		if len(tmp) == 0:
			if repeat == _CRYSOL_RETRY:
				return False,(pdb,"Failed to calculate SAXS profile after %i tries."%_CRYSOL_RETRY)
			else:
				return self.calculate(pdb, repeat+1)

		out = os.path.join(self.outputdir,"%s.dat"%name)
		try:
			fpi,fpo = open(tmp[0]),open(out,'w')		
			for l in fpi.readlines()[1:-1]:
				fpo.write( "%s\n" % ("\t".join( l.split()[0:2] ) ) )
			fpi.close()
			fpo.close()
		except Exception as e:
			return False,(pdb,"Could not clean up CRYSOL profile: %s"%e)

		if not os.path.exists( out ):
			return False,(pdb,"Failed to extract SAXS profile after %i tries."%_CRYSOL_RETRY)
			
		return True,(pdb,None)
