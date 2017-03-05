import os
import argparse

try:
	import IMP
	import IMP.atom
	import IMP.core
	import IMP.saxs
except:
	IMP = None
	import os
	import shutil
	import argparse
	import subprocess
	import tempfile

from threading import Timer

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeListFromOptions

_FOXS_TIMER = 10000 # time to wait for foxs to finish calculating (in ms)

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'SAXS - FoXS'
		self.version = '1.0.2'
		self.types = ('SAXS',)

		self.parser = argparse.ArgumentParser(prog=self.name)
		#self.parser.add_argument('-qmin',	metavar='Min q',	type=float,	default=0.0,	help='Minimum scattering angle')
		#self.parser.add_argument('-qmax',	metavar='Max q',	type=float,	default=0.5,	help='Maximum scattering angle')
		#self.parser.add_argument('-qnum',	metavar="q Points",	type=int,	default=100,	help='Total points in the scattering profile')
		self.parser.add_argument('-q',	metavar='Max q',	type=float,	default=0.5,	help='Maximum scattering angle')
		self.parser.add_argument('-s',	metavar="Points",	type=int,	default=100,	help='Total points in the scattering profile')
		
		if IMP != None:
			self.info = 'This plugin uses the Integrative Modeling Platform (see http://salilab.org/imp) to predict SAXS profiles from PDBs.'
			self.parser.add_argument('-water',	action='store_true',	default=True,			help='Use hydration layer') # there's a bug in FoXS that may cause a crash with this option 
		else:
			self.info = 'This plugin uses the external program FoXS (see http://salilab.org/imp) to predict SAXS profiles from PDBs.'
			self.path = 'foxs'

	def setup(self, parent, options, outputpath):
		self.options	= options
		self.args		= self.parser.parse_args( makeListFromOptions(self.options) )
		self.outputpath	= outputpath
		
		# initialize some IMP objects
		if IMP:
			self.IMP_model	= IMP.kernel.Model()
			self.IMP_sas	= IMP.saxs.SolventAccessibleSurface()
		else:
			try:
				sub = subprocess.Popen([self.path,'--version'], stdout=subprocess.PIPE)
				output,err = sub.communicate()
				code = sub.wait()
			except Exception as e:
				if(e.errno == os.errno.ENOENT):
					raise mesPluginError("Could not find \"foxs\" excecutable, is it installed?")
				else:
					raise e
					
		return True

	def calculate(self, pdb):
		if IMP:
			return self.calculate_IMP(pdb)
		else:
			return self.calculate_FoXS(pdb)

	def calculate_IMP(self, pdb):
		mp = IMP.atom.read_pdb( pdb, self.IMP_model, IMP.atom.NonWaterNonHydrogenPDBSelector(), True, True )
		
		particles = IMP.atom.get_by_type(mp, IMP.atom.ATOM_TYPE )
#		profile = IMP.saxs.Profile( self.args.qmin, self.args.qmax, (self.args.qmax - self.args.qmin) / self.args.qnum )
		profile = IMP.saxs.Profile( 0.0, self.args.q, (self.args.q - 0.0) / self.args.s )
		
		if( self.args.water ):
			ft = IMP.saxs.get_default_form_factor_table()
			for i in range(0, len(particles) ):
				radius = ft.get_radius(particles[i])
				IMP.core.XYZR.setup_particle(particles[i], radius)
			profile.calculate_profile_partial( particles, self.IMP_sas.get_solvent_accessibility(IMP.core.XYZRs(particles)) )
		else:
			profile.calculate_profile( particles )
		
		out = os.path.join(self.outputpath, "%s.dat" % (os.path.splitext(os.path.basename(pdb))[0]))
		profile.write_SAXS_file( out, self.args.qmax )
		
		return True,(pdb,None)
		
	def calculate_FoXS(self, pdb, repeat=0):
		base = os.path.basename(pdb)
		name = os.path.splitext( base )[0]

		if not os.path.exists(pdb):
			return False,(pdb,"Could not read file.")

		cmd = [self.path]
		cmd.extend( makeListFromOptions(self.options) )
		cmd.append( base )
		
		try:
			print " ".join(cmd)
			sub = subprocess.Popen(cmd, cwd=os.path.dirname(pdb))
			
			# timer to make sure foxs call does not hang
			kill_proc = lambda p: p.kill()
			timer = Timer(_FOXS_TIMER/1000, kill_proc, [sub])
			timer.start()
			sub.wait()
			timer.cancel()

		except Exception as e:
			return False,(pdb,"Error calling \"foxs\": %s" %e)
				
		if not os.path.exists( "%s.dat"%(pdb) ):
			output,err = sub.communicate()
			return False,(pdb,"FoXS failed to calculate a SAXS profile: %s"%output)
		
		try:
			os.remove( os.path.join(os.path.dirname(pdb),"%s.plt"%name) )
		except OSError:
			pass # this may change in later FoXS versions.
#			return False,(pdb,"Could not remove plot file: %s"%e)
		
		try:
			shutil.move( "%s.dat"%(pdb), os.path.join(self.outputdir,"%s.dat"%name) )
		except Exception as e:
			return False,(pdb,"Could not move calculated SAXS profile file: %s"%e)
			
		return True,(pdb,None)