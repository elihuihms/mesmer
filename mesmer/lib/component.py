import os
import glob

from mesmer.errors import *
from mesmer.lib.input import get_input_blocks

class Attribute:

	def __init__(self, restraint):
		self.restraint = restraint
		self.data = {}
		return

class Component:
	"""
	Contains the various attributes (stoichiometries, SAXS profiles, absorbance curves, etc.) of a given component
	"""

	def __init__(self, logger):
		"""
		Initialize the component

		1. Sets name to an empty string
		2. Sets attributes to an empty list
		3. Sets plugin_data to an empty dict
		"""

		self.logger = logger
		self.name = ''
		self.attributes = []
		self.plugin_data = {}
		return

	def load(self, file, plugins, targets):
		"""
		Load the component's various attributes from a specified file using plugins

		Returns True on success, or False on Failure, errors are communicated via the print_msg function

		Arguments:
			file	- A path to a MESMER component file, see general_functions.get_input_blocks() for more information
			plugins	- A list of plugin modules for interpretation of data and creation of mesAttribute objects
			targets	- A list of targets, which are used to properly format the object's attributes (e.g. interpolation of curves, etc.)
		"""

		blocks = get_input_blocks(file)

		if( blocks == None ):
			raise mesComponentError("Could not read component file \"%s\"." % (file))
		elif( len(blocks) == 0 ):
			raise mesComponentError("Component file \"%s\" contains no recognizable data." % (file))

		# make a checklist of the requested target restraints (by plugin name) each component must satisfy
		checklist = {}
		for r in targets[0].restraints:
			if(r.type in checklist):
				checklist[r.type] += 1
			else:
				checklist[r.type] = 1

		# find the plugin that handles this type of of data
		for b in blocks:

			if(b['type'] == 'NAME'):
				self.name = b['header'][1]
				continue

			for p in plugins:
				if(b['type'] in p.types):

					# initialize the plugin storage variable for this restraint type
					self.plugin_data[b['type']] = None

					# create a new attribute linked to the proper type of restraint
					for r in targets[0].restraints:
						if(b['type'] == r.type):

							attribute = Attribute(r)

							try:
								messages = p.load_attribute( attribute, b, self.plugin_data[b['type']] )
							except mesPluginError as e:
								self.logger.error("Plugin \"%s\" could not create an attribute from the component file \"%s\" lines %i-%i, reported that \"%s\"." % (
									p.name,
									file,
									b['l_start'],
									b['l_end'],
									e.msg))
								return False

							self.attributes.append(attribute)

							self.logger.debug("Component file \"%s\" lines %i-%i - plugin \"%s\" created \"%s\" restraint." % (
								file,
								b['l_start'],
								b['l_end'],
								p.name,
								b['type']))

							for m in messages:
								self.logger.debug("Plugin \"%s\" reported: %s" % (p.name,m))

							# decrement the checklist for this restraint type
							checklist[ b['type'] ] -= 1

							# only allow one plugin per block
							break

		if( self.name == '' ):
			raise mesComponentError("Component file \"%s\" has no NAME attribute." % (file) )
			return False

		# go through our checklist and ensure that all target restraint types are present
		for (k,v) in checklist.iteritems():
			if(v != 0):
				raise mesComponentError("Component file \"%s\" is missing %i \"%s\" restraint type(s)." % (file,v,k))
				return False

		return True

def load_components( logger, args, plugins, targets, print_status=True ):

	files = []
	for f in args.components:

		if( os.path.isdir(f[0]) ):
			files.extend( glob.glob( "%s%s*" % (f[0],os.sep) ) )
		elif( os.path.isfile(f[0]) ):
			files.extend( f[0] )
		else:
			raise mesComponentError("Specified component or directory \"%s\" does not exist" % f[0])

	if(len(files) == 0):
		raise mesComponentError("No components specified.")

	logger.info("Found %i component files." % (len(files)))
	components = {}

	names = [''] * len(files)
	divisor = int(max(len(files)/10,1))
	for (i,f) in enumerate(files):

		if print_status and i % divisor == 0:
			logger.debug("Component loading progress: %i%%" % (100*i/len(files)) )

		temp = Component(logger)

		if( not temp.load(f,plugins,targets) ):
			raise mesComponentError("\nERROR:\tCould not load component file \"%s\"." % (f))

		if( temp.name in names ):
			raise mesComponentError("\nERROR:\tComponent file \"%s\" has the same NAME as a previous component." % (f))

		# add the component to the component database
		components[temp.name] = temp
		names[i] = temp.name
	if print_status:
			logger.info("Component loading progress: 100%")

	return components
