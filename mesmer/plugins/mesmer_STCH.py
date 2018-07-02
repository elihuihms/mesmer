"""MESMER plugin for component stoichiometry

Target file arguments:
-component <name> <# of component>

Component file arguments:
-component <name> <# of component>
"""

import scipy

from argparse import ArgumentError
from StringIO import StringIO

from mesmer.errors import *
from mesmer.lib.plugin import *
from mesmer.lib.fitting import *

class plugin( TargetPlugin ):

	def __init__(self, *args, **kwargs):
		super(plugin, self).__init__()

		self.name = 'default_STCH'
		self.version = '1.1.0'
		self.info = 'This plugin compares experimental and predicted stoichiometry of the components present in multicomponent mixtures.'
		self.types = ('STCH','STCH0','STCH1','STCH2','STCH3','STCH4','STCH5','STCH6','STCH7','STCH8','STCH9')

		self.target_parser.add_argument('-scale',	default=1.0, type=float, metavar='1.0', help='')
		self.target_parser.add_argument('-component', nargs='+', metavar='NAME, #', action='append', help='')

		self.component_parser.add_argument('-component', nargs='+', metavar='NAME, #', action='append', help='')

	def load_restraint( self, restraint, block, target_data ):
		try:
			args = self.target_parser.parse_args(block['header'][2:])
		except ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		total = 0.0
		restraint.data['components'] = {}
		for component in args.component:
			restraint.data['components'][component[0]] = float(component[1])
			total += float(component[1])

		# normalize the components to ratios
		for component in args.component:
			restraint.data['components'][component[0]] /= total

		target_data['args'] = args

		return []

	def load_attribute( self, attribute, block, ensemble_data ):
		try:
			args = self.component_parser.parse_args(block['header'][1:])
		except ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		attribute.data['components'] = {}
		for component in args.component:
			attribute.data['components'][component[0]] = float(component[1])

		return []

	def load_bootstrap( self, bootstrap, restraint, ensemble_data, target_data ):
		bootstrap.data['components'] = {}
		for name in restraint.data['components']:
			bootstrap.data['components'][name] = ensemble_data['components'][name]

		return []

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		assert(len(attributes) == len(ratios))

		# convert component count to ratios
		total = 0.0
		ensemble_data['components'] = {}
		for name in restraint.data['components']:
			ensemble_data['components'][name] = 0.0

			for (i,a) in enumerate(attributes):
				if(name in a.data['components']):
					ensemble_data['components'][name] += (a.data['components'][name] * ratios[i])
					total += (a.data['components'][name] * ratios[i])

		fitness = 0.0

		# create score from flat harmonic
		for name in restraint.data['components']:
			if( total == 0.0 ):
				ensemble_data['components'][name] = 0.0
			else:
				ensemble_data['components'][name] /= total

			#fitness += tools.get_flat_harmonic( restraint.data['components'][name], restraint.data['components'][name], ensemble_data['components'][name] )

			# Wolfgang Rieping, Michael Habeck, and Michael Nilges, JACS 11/01/2005
			if( ensemble_data['components'][name] ) > 0:
				fitness += scipy.fabs( target_data['args'].scale * scipy.log(restraint.data['components'][name] / ensemble_data['components'][name]) )
			else:
				fitness += 1.0

		return fitness

