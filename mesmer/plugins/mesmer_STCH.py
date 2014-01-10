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
		self.version = '2013.11.13'
		self.type = ('STCH','STCH0','STCH1','STCH2','STCH3','STCH4','STCH5','STCH6','STCH7','STCH8','STCH9')

	#
	# output functions
	#

	def ensemble_state( self, restraint, target_data , ensemble_data, file_path):
		"""
		Prints the status of the plugin for the current generation and target

		Returns a list of Error_state,output

		Arguments:
		target_data		- list of data the plugin has saved for the target
		ensemble_data	- list of data the plugin has saved for every ensemble in the run, ordered by overall fitness
		filePath		- an optional file path the plugin can save data to
		"""

		return []
	#
	# data handling functions
	#

	def load_restraint( self, restraint, block, target_data ):
		"""
		Initializes the provided restraint with information from the target file

		Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).

		Arguments:
		target_data	- The plugin's data storage variable for the target
		block		- The block dict provided by MESMER (see the mesRestraint docstring for more information)
		restraint	- The empty restraint object to be filled
		"""

		# block dictionary format:
		#
		# "type"	- string, corresponds to a type handled by this plugin
		# "header"	- string, containing the first line of the content block
		# "content"	- list of strings, containing the rest of the content block (if any)
		# "l_start" - integer, the line index for the start of the content block from the original file
		# "l_end"	- integer, the line index for the end of the content block from the original file

		# example header format:
		# TYPE	SCALE	OPTIONS
		# TEST	1		-value <N>

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
		"""
		Initializes the provided attribute with information from a component file

		Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).

		Arguments:
		ensemble_data	- The plugin's data storage variable for this ensemble
		block			- The block dict provided by MESMER
		attribute		- The empty attribute object to be filled
		"""

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
		"""
		Generates a bootstrap restraint using the provided ensemble data

		Arguments:
		bootstrap		- mesRestraint, the restraint to fill with the bootstrap sample
		restraint		- mesRestraint, the restraint serving as the template for the sample
		ensemble_data	- The plugin's data storage variable for this ensemble
		target_data		- The plugin's data storage variable for the target
		"""

		bootstrap.data['components'] = {}
		for name in restraint.data['components']:
			bootstrap.data['components'][name] = ensemble_data['components'][name]

		return []

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		"""
		Calculates the fitness of a set of attributes against a given restraint

		Returns a fitness score.

		Arguments:
		ensemble_data	- The plugin's data storage variable for the ensemble
		restraint		- The restraint object to be fitted against
		attrbutes		- A list of attributes to be averaged together and compared to the restraint
		ratios			- The relative weighting (ratio) of each attribute
		"""

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

