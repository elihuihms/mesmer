import os
import argparse

import IMP
import IMP.atom
import IMP.core
import IMP.saxs

from lib.gui.plugin_objects import guiCalcPlugin
from lib.gui.tools_plugin	import makeListFromOptions

class plugin(guiCalcPlugin):

	def __init__(self):
		guiCalcPlugin.__init__(self)
		self.name = 'SAXS - FoXS'
		self.version = '2015.06.23'
		self.info = 'This plugin uses the Integrative Modeling Platform (see http://salilab.org/imp) to predict a SAXS profile from a PDB.'
		self.type = 'SAXS'

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-qmin',	metavar='Min q',	type=float,	default=0.0,	help='Minimum scattering angle')
		self.parser.add_argument('-qmax',	metavar='Max q',	type=float,	default=0.5,	help='Maximum scattering angle')
		self.parser.add_argument('-qnum',	metavar="q Points",	type=int,	default=100,	help='Total points in the scattering profile')
		self.parser.add_argument('-water',	action='store_true',	default=True,			help='Use hydration layer')

	def setup(self, parent, options, outputpath):
		self.args		= self.parser.parse_args( makeListFromOptions(options) )
		self.outputpath	= outputpath
		
		# initialize some IMP objects
		self.IMP_model	= IMP.kernel.Model()
		self.IMP_sas	= IMP.saxs.SolventAccessibleSurface()
		return True

	def calculate(self, pdb):
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
		
		out = "%s%s%s.dat" % (self.outputpath, os.sep, os.path.splitext(os.path.basename(pdb))[0])
		profile.write_SAXS_file( out, self.args.qmax )
		
		return True,(pdb,None)