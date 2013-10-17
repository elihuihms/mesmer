import re
import random

from exceptions			import *
from utility_functions	import print_msg,get_input_blocks

class mesAttribute:

	def __init__(self, restraint):
		self.restraint = restraint
		self.data = {}
		return

class mesComponent:
	"""
	Contains the various attributes (stoichiometries, SAXS profiles, absorbance curves, etc.) of a given component
	"""

	def __init__(self):
		"""
		Initialize the component

		1. Sets name to an empty string
		2. Sets attributes to an empty list
		3. Sets plugin_data to an empty dict
		"""

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
			print_msg("ERROR: Could not read component file \"%s\"." % (file))
		elif( len(blocks) == 0 ):
			print_msg("ERROR: Component file \"%s\" contains no recognizable data." % (file))

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
				self.name = re.split("\s+",b['header'])[1]
				continue

			for p in plugins:
				if(b['type'] in p.type):

					# initialize the plugin storage variable for this restraint type
					self.plugin_data[b['type']] = None

					# create a new attribute linked to the proper type of restraint
					for r in targets[0].restraints:
						if(b['type'] == r.type):

							attribute = mesAttribute(r)

							try:
								messages = p.load_attribute( attribute, b, self.plugin_data[b['type']] )
							except mesPluginError as e:
								print_msg("ERROR: plugin \"%s\" could not create an attribute from the component file \"%s\" lines %i-%i" % (p.name,file,b['l_start'],b['l_end']))
								print_msg("ERROR: plugin \"%s\" reported: %s" % (p.name,e.msg))
								return False

							for m in messages:
								print_msg("INFO: plugin \"%s\" reported: %s" % (p.name,m))

							self.attributes.append(attribute)

							# decrement the checklist for this restraint type
							checklist[ b['type'] ] -= 1

							# only allow one plugin per block
							break

		if( self.name == '' ):
			print_msg("ERROR: component file \"%s\" has no NAME attribute." % (file) )
			return False

		# go through our checklist and ensure that all target restraint types are present
		for (k,v) in checklist.iteritems():
			if(v != 0):
				print_msg("ERROR: component file \"%s\" is missing %i \"%s\" restraint type(s)." % (file,v,k))
				return False

		return True
