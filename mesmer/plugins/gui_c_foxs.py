import os
import argparse

import IMP
import IMP.atom
import IMP.core
import IMP.saxs

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		self.name = 'SAXS - FoXS'
		self.version = '2014.03.03'
		self.type = 'SAXS'
		self.respawn = 20

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-qmin',	type=float,	default=0.0,	help='Minimum scattering angle')
		self.parser.add_argument('-qmax',	type=float,	default=0.5,	help='Maximum scattering angle')
		self.parser.add_argument('-qnum',	type=int,	default=100,	help='Total points in the scattering profile')
		self.parser.add_argument('-water',	action='store_true',	default=True,	help='Use hydration layer')

	def setup(self, pdbs, dir, options, threads):
		self.args		= self.parser.parse_args( makeStringFromOptions(options).split() )
		self.pdbs		= pdbs
		self.dir		= dir
		self.options	= options
		self.threads	= threads
		self.counter	= 0
		self.state		= 0 # not busy
		self.currentPDB = ''
		
		# initialize some IMP objects
		self.IMP_model	= IMP.kernel.Model()
		self.IMP_sas	= IMP.saxs.SolventAccessibleSurface()


	def calculator(self):
		if(self.state >= self.threads):	#semaphore to check if we're still busy processing
			return
		self.state +=1

		pdb = os.path.abspath( self.pdbs[self.counter] )
		if not os.path.exists(pdb):
			raise Exception( "Could not find \"%s\"" % (pdb) )

		mp = IMP.atom.read_pdb( pdb, self.IMP_model, IMP.atom.NonWaterNonHydrogenPDBSelector(), True, True )
		
		particles = IMP.atom.get_by_type(mp, IMP.atom.ATOM_TYPE )
		profile = IMP.saxs.Profile( self.args.qmin, self.args.qmax, (self.args.qmax - self.args.qmin) / self.args.qnum )
		
		if( self.args.water ):
			ft = IMP.saxs.default_form_factor_table()
			for i in range(0, len(particles) ):
				radius = ft.get_radius(particles[i])
				IMP.core.XYZR.setup_particle(particles[i], radius)
			profile.calculate_profile_partial( particles, self.IMP_sas.get_solvent_accessibility(IMP.core.XYZRs(particles)) )
		else:
			profile.calculate_profile( particles )
		
		out = "%s%s%s.dat" % (self.dir, os.sep, os.path.splitext(os.path.basename(pdb))[0])
		profile.write_SAXS_file( out, self.args.qmax )
		
		self.state -=1
		self.counter +=1
		return self.counter
