import sys
import os
import imp
import glob
import argparse
import re
import collections

from mesmer.errors import *

class Plugin(object):
	"""A class primitive for all plugins and utilities used in MESMER
	
	Attributes:
		name (string): (Required) Brief name of the plugin (inherited from MESMERPlugin)
		version (string): (Required) Version string of the plugin (inherited from MESMERPlugin)
		info (string): (Required) User-friendly information about the plugin (inherited from MESMERPlugin)
		parser (Argparse parser): Argument parser for user-selectable options
	"""
	
	def __init__(self):		
		self.name = ''
		self.version = ''
		self.info = ''
		self.parser = argparse.ArgumentParser()

	def unload(self):
		"""Empty stub for now, should throw a mesPluginError if there's an issue."""
		pass
	
	def strip_parser_tags(self, parser=None, excludes=[] ):
		if parser == None:
			parser = self.parser
		for action in parser._actions:
			if action.__dict__['help'] == None:
				continue
			action.__dict__['help'] = re.sub(r' \#[a-zA-Z_]+', '', action.__dict__['help'])

	def get_argument_dict(self,parser=None,tag=None):
		"""Convert an argparse argument parser to a dict
	
		Args:
			parser (argparse.ArgumentParser): Parser to construct dict from. If None, return the plugin's arguments
			tag (string): Only display arguments tagged with the specified tag (None for all arguments). This is useful for returning a subset of arguments when the plugin is used in different contexts.
	
		Returns: dict representation of parser's arguments"""
	
		if parser == None:
			parser = self.parser
	
		options,savetypes = collections.OrderedDict([]),('help','option_strings','choices','type','dest','default','choices','required','nargs','metavar')
		for action in parser._actions:
			if action.dest == 'help':
				continue

			if tag != None:
				if tag not in action.help:
					continue
				else:
					action.help = action.help.replace(tag,'')	
							
			options[ action.dest ] = {}
			for key in savetypes:
				options[ action.dest ][ key ] = getattr(action,key,None)
			options[ action.dest ]['value'] = ''
			options[ action.dest ]['group'] = action.container.title

		return options

	def get_argument_list(self,parser=None,tag=None):
		ret = []
		for k,o in self.get_argument_dict(parser,tag).iteritems():
			if(o['nargs'] == 0):
				if o['value']:
					ret.append( o['option_strings'][0] )
			elif( o['value'] == None or o['value'] == 'None' or o['value'] == '' ):
				if o['required']:
					raise mesPluginError("Encountered a required option without a value: %s" % o['dest'])
			elif(o['nargs'] == None):
				ret.append( o['option_strings'][0] )
				ret.append( str(o['value']) )
			else:
				raise mesPluginError("Encountered an option that could not be converted to a string properly: %s" % o['dest'])
		return ret

def load_plugins( basedir, type, disabled=[], args=[] ):
	"""Find all plugin (plugin_*.py) files in the provided directory, and return dict
	
	Returned list format tuples:
		id (string): The ID of the plugin (obtained from filename)
		ok (bool): Whether or not there were any exceptions raised while loading the plugin module
		info (string): Informative text about the plugin
		plugin (module): The actual plugin module (IF ok==True, otherwise None)
	
	Args:
		basedir (string): Path to MESMER directory
		type (string): Plugin type, is used to discriminate plugin file paths
		disabled (list): List of plugin IDs to ignore
		arguments (ArgumentParser namespace): MESMER arguments
	
	Returns: dict of plugin tuples
	"""

	plugin_dir = os.path.join(basedir, 'plugins')
				
	ret = []
	for f in glob.glob( '%s%s%s_*.py' % (plugin_dir,os.sep,type) ):

		id, ext = os.path.splitext(os.path.basename(f))
		if id in disabled:
			continue
		
		try:
			file, filename, data = imp.find_module(id, [plugin_dir])
		except ImportError:
			ret.append( (id, False, "Could not discover plugin at path \"%s\"." % plugin_dir, None) )
			continue

		try:
			module = imp.load_module(id, file, filename, data)
		except:
			ret.append( (id, False, "Could not import plugin module \"%s\". Reason: %s" % (id,sys.exc_info()[1]), None) )
			continue
		finally:
			file.close()

		# some plugins may need access to command line arguments
		try:
			ret.append( (id, True, '', module.plugin( *args )) )
		except:
			ret.append( (id, False, "Could not load plugin \"%s\". Reason: %s" % (id,sys.exc_info()[1]), None) )
				
	return ret

def unload_plugins( plugins ):
	for p in plugins:
		try:
			p.unload()
		except mesPluginError:
			raise mesPluginError("WARNING:\tPlugin \"%s\" unloading failed: %s" % (p.name,sys.exc_info()[1]))
		del p