"""
MESMER plugin for component stoichiometry

Target file arguments:
-component <name> <# of component>

Component file arguments:
-component <name> <# of component>
"""

import argparse
import math

from lib.plugin_objects import mesPluginError,mesPluginBasic
import lib.plugin_tools as tools

class plugin( mesPluginBasic ):

	def __init__(self, args):
		mesPluginBasic.__init__(self, args)

		self.name = 'default_STCH'
		self.version = '2015.06.23'
		self.info = 'This plugin compares experimental and predicted stoichiometry of the components present in multicomponent mixtures.'
		self.type = ('STCH','STCH0','STCH1','STCH2','STCH3','STCH4','STCH5','STCH6','STCH7','STCH8','STCH9')

	def load_restraint( self, restraint, block, target_data ):
		parser = argparse.ArgumentParser(prog=self.type[0])
		parser.add_argument('-scale',		default=1.0, type=float, metavar='1.0', help='')
		parser.add_argument('-component', nargs='+', metavar='NAME, #', action='append', help='')

		try:
			args = parser.parse_args(block['header'].split()[2:])
		except argparse.ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		sum = 0.0
		restraint.data['components']	= {}
		for component in args.component:
			restraint.data['components'][component[0]] = float(component[1])
			sum += float(component[1])

		# normalize the components to ratios
		for component in args.component:
			restraint.data['components'][component[0]] /= sum

		target_data['args'] = args

		return []

	def load_attribute( self, attribute, block, ensemble_data ):
		parser = argparse.ArgumentParser(prog=self.name)
		parser.add_argument('-component', nargs='+', metavar='NAME, #', action='append', help='')

		try:
			args = parser.parse_args(block['header'].split()[1:])
		except argparse.ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		attribute.data['components']	= {}
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
		sum = 0.0
		ensemble_data['components'] = {}
		for name in restraint.data['components']:
			ensemble_data['components'][name] = 0.0

			for (i,a) in enumerate(attributes):
				if(name in a.data['components']):
					ensemble_data['components'][name] += (a.data['components'][name] * ratios[i])
					sum += (a.data['components'][name] * ratios[i])

		fitness = 0.0

		# create score from flat harmonic
		for name in restraint.data['components']:
			if( sum == 0.0 ):
				ensemble_data['components'][name] = 0.0
			else:
				ensemble_data['components'][name] /= sum

			#fitness += tools.get_flat_harmonic( restraint.data['components'][name], restraint.data['components'][name], ensemble_data['components'][name] )

			# Wolfgang Rieping, Michael Habeck, and Michael Nilges, JACS 11/01/2005
			if( ensemble_data['components'][name] ) > 0:
				fitness += math.fabs( target_data['args'].scale * math.log(restraint.data['components'][name] / ensemble_data['components'][name]) )
			else:
				fitness += 1.0

		return fitness

