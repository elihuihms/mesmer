import os
import argparse
import shutil

from subprocess			import Popen,PIPE

from gui.plugin_objects import guiCalcPlugin
from gui.tools_general	import getWhichPath
from gui.tools_plugin	import makeStringFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'SAXS - Crysol'
		self.version = '2013.09.13'
		self.type = 'SAXS'
		self.respawn = 100

		self.parser = argparse.ArgumentParser(prog=self.name)
		#self.parser.add_argument('-lm',		default='',	help='Maximum order of harmonics (default 15)')
		#self.parser.add_argument('-fb',		default='',	help='Order of fibonacci grid(default 17)')
		self.parser.add_argument('-sm',		type=float,	default=0.5,	help='Maximum scattering vector')
		self.parser.add_argument('-ns',		type=int,	default=128,	help='# points in the computed curve')
		self.parser.add_argument('-dns',	type=float,	default=0.334,	help='Solvent density (default 0.334 e/A**3)')
		self.parser.add_argument('-dro',	type=float,	default=0.03,	help='Contrast of hydration shell (default 0.03 e/A**3)')
		self.parser.add_argument('-eh',		action='store_true', 		help='Account for explicit hydrogens')

	def setup(self, pdbs, dir, options):
		self.pdbs	= pdbs
		self.dir	= dir
		self.options	= options
		self.counter	= 0
		self.state	= 0 # not busy
		self.currentPDB = ''

		self.prog = getWhichPath( 'crysol' )
		if(self.prog == ''):
			raise Exception("Could not find \"crysol\" program. Perhaps it isn't installed?")

	def calculator(self):
		if(self.state != 0):	#semaphore to check if we're still busy processing
			return
		self.state = 1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		base = os.path.basename(pdb)
		name = os.path.splitext( os.path.basename(pdb) )[0]

		if not os.path.exists(pdb):
			raise Exception( "Could not find \"%s\"" % (pdb) )

		try:
			shutil.copy(pdb,self.dir)
		except:
			raise SAXSCalcException( "Could not copy \"%s\" into directory \"%s\"" % (pdb,self.dir) )

		cmd = [self.prog]
		cmd.extend( makeStringFromOptions(self.options).split() )
		cmd.append( base )
		pipe = Popen(cmd, cwd=self.dir, stdout=PIPE)
		pipe.wait()

		try:
			os.remove( "%s%s%s" % (self.dir,os.sep,base) )
		except:
			raise Exception( "Could not remove temporary PDB \"%s\" from directory \%s\" " % (base,self.dir) )

		tmp = "%s%s%s00.int" % (self.dir,os.sep,name)
		if not os.path.exists(tmp):
			raise Exception( "Failed to calculate SAXS profile for \"%s\". CRYSOL output: %s" % (pdb,pipe.stdout.read()) )

		try:
			lines = open( tmp ).readlines()[1:-1]
			f = open( "%s%s%s.dat" % (self.dir,os.sep,name), 'w' )
			for l in lines:
				f.write( "%s\n" % ("\t".join( l.split()[0:2] ) ) )
			f.close()
		except:
			raise Exception( "Could not clean up CRYSOL profile \"%s\"" % (tmp) )

		os.remove("%s%s%s00.log" % (self.dir,os.sep,name) )
		os.remove("%s%s%s00.alm" % (self.dir,os.sep,name) )
		os.remove("%s%s%s00.int" % (self.dir,os.sep,name) )

		self.state = 0
		self.counter +=1
		return self.counter
