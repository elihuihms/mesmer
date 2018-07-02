import re
import copy

from mesmer.errors import *
from mesmer.lib.input import get_input_blocks

class Restraint(object):
	"""
	A basic object for holding information about a restraint
	"""
	def __init__(self, scale, type):
		self.scale = scale
		self.type = type
		self.data = {}
		return

class Target(object):
	"""
	Contains the various types of experimental data (restraints) that will be used as a target for fitting
	"""

	def __init__(self,logger):
		"""
		Initialize the target

		1. Sets name to an empty string
		2. Sets restraints to an empty list
		3. Sets plugin_data to an empty dict
		"""

		self.logger = logger
		self.name = ''
		self.restraints = []
		self.plugin_data = {}

		return

	def load(self, file, plugins):
		"""
		Load the targets's restraints from a specified file using plugins

		Args:
			file (string): Path to a MESMER target file, see general_functions.get_input_blocks() for more information
			plugins (list): List of mesPlugin modules for interpretation of data and creation of Restraint objects

		Returns: True on success, or False on Failure, errors are communicated via the print_msg function
		"""

		# get an array of data blocks from the provided target
		blocks = get_input_blocks(file)

		if( not blocks ):
			raise mesTargetError("Could not read target file \"%s\"." % (file))

		if( len(blocks) == 0 ):
			raise mesTargetError("Target file \"%s\" contains no recognizable data." % (file))

		# find the plugin that handles this type of of data
		for b in blocks:

			if(b['type'] == 'NAME'):
				self.name = b['header'][1]
				continue

			for p in plugins:
				if(b['type'] in p.types):

					# initialize the plugin storage variable for this restraint type
					self.plugin_data[b['type']] = {}

					status = None

					# check that the restraint scaling factor is present
					try:
						weighting = float(b['header'][1])
					except:
						raise mesTargetError("Restraint on line %i does not have a weighting value." % (b['l_start']))

					# create a new restraint
					restraint = Restraint(weighting, b['type'])

					try:
						messages = p.load_restraint( restraint, b, self.plugin_data[b['type']] )
					except mesPluginError as e:
						self.logger.error("Plugin \"%s\" could not create a restraint from the target file \"%s\" lines %i-%i, reported \"%s\"." % (
							p.name,
							file,
							b['l_start'],
							b['l_end'],
							e.msg))
						return False

					self.restraints.append(restraint)
					
					self.logger.info("Target file \"%s\" lines %i-%i - plugin \"%s\" created %.1fx weighted \"%s\" restraint." % (
						file,
						b['l_start'],
						b['l_end'],
						p.name,
						weighting,
						b['type']))
			
					for m in messages:
						self.logger.info("Plugin \"%s\" reported: %s" % (p.name,m))

					# only allow one plugin per block
					break

		if( self.name == '' ):
			raise mesTargetError("component file \"%s\" has no NAME attribute." % (file) )

		return True

	def make_bootstrap( self, plugins, ensemble ):
		"""
		Create a bootstrap estimate clone of self

		Args:
			plugins (list): A list of mesPlugin modules
			ensemble: The ensemble used to create the estimate

		Returns: a Target clone with bootstrapped estimates of all restraints

		@TODO@ Error handling
		"""

		dupe = copy.copy(self)

		for r in dupe.restraints:
			for p in plugins:
				if(r.type in p.types):
					p.load_bootstrap( r, r, ensemble.plugin_data[dupe.name][r.type], dupe.plugin_data[r.type] )

		return dupe

def load_targets( logger, args, plugins ):
	"""
	Loads all targets specified in the args by passing them off to the appropriate plugins
	"""

	if(len(args.target) < 0):
		raise mesTargetError("No targets specified.")

	names, targets = [], []

	for f in args.target:
		logger.info("Reading target file \"%s\"." % (f))

		targets.append( Target(logger) )

		if( not targets[-1].load(f,plugins) ):
			raise mesTargetError("Could not load target file \"%s\"." % (f))

		if( targets[-1].name in names ):
			raise mesTargetError("Target file \"%s\" has the same name (%s) as a previous target." % (f,targets[-1].name))

		names.append(targets[-1].name)

	for t in targets:
		if( len(targets[0].restraints) != len(t.restraints) ):
			raise mesTargetError("All targets in titration analysis must have the same number of restraints.")

	return targets
