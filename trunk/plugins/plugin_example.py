"""
Example MESMER plugin

Target file arguments:
-value <N>

Component file arguments:
-value <N>
"""

from argparse import ArgumentParser
from lib.plugin_primitives import plugin_basic

class plugin( plugin_basic ):

	name = 'XX_EXAMPLE'
	version = '2013.06.04'
	type = ['TEST']

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

		output = (
		'Example plugin',
		'Path is %s' % (file_path)
		)

		return (True,output)
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

		parser = ArgumentParser(prog=self.type[0])
		parser.add_argument('-value', metavar='number', help='')

		try:
			args = parser.parse_args(block['header'].split()[2:])
		except argparse.ArgumentError, exc:
			return (False,["Argument error: %s" % exc.message()])

		target_data['args']		= args
		restraint.data['value']	= args.value

		return (True,[])

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
		parser.add_argument('-value', metavar='number', help='')

		try:
			args = parser.parse_args(block['header'].split()[1:])
		except argparse.ArgumentError, exc:
			return (False,["Argument error: %s" % exc.message()])

		attribute.data['value'] = args.value

		return (True,[])

	def load_bootstrap( self, bootstrap, restraint, ensemble_data, target_data ):
		"""
		Generates a bootstrap restraint using the provided ensemble data

		Arguments:
		bootstrap		- mesRestraint, the restraint to fill with the bootstrap sample
		restraint		- mesRestraint, the restraint serving as the template for the sample
		ensemble_data	- The plugin's data storage variable for this ensemble
		target_data		- The plugin's data storage variable for the target
		"""

		bootstrap.data['value'] = restraint.data['value']

		return (True,[])

	#
	# Calc fitness - the heart of the plugin, provides the fitness of an ensemble
	#

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		"""
		Calculates the fitness of a set of attributes against a given restraint

		Returns a fitness score, ideally a chi-square error (1=good fit, or >1 if bad fit). Less ideally a sum-squared of error.

		Arguments:
		ensemble_data	- The plugin's data storage variable for the ensemble
		restraint		- The restraint object to be fitted against
		attrbutes		- A list of attributes to be averaged together and compared to the restraint
		ratios			- The relative weighting (ratio) of each attribute
		"""

		assert(len(attributes) == len(ratios))

		avg = 0.0
		for (i,a) in enumerate(attributes):
			avg += a.data['value'] * ratios[i]

		return restraint.data['value'] - avg

