import sys
import os
import imp
import glob

from exceptions import *

def load_plugins( basedir, type, disabled=[], args=None ):
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
		args (ArgumentParser namespace): MESMER arguments
	
	Returns: dict of plugin tuples
	"""

	plugin_dir = os.path.join(basedir, 'plugins')

	# some plugins may need access to command line args
	if args is None:
		args = []
	else:
		args = [args]
				
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

		try:
			ret.append( (id, True, '', module.plugin( *args )) )
		except:
			ret.append( (id, False, "Could not load plugin \"%s\". Reason: %s" % (id,sys.exc_info()[1]), None) )
				
	return ret

def unload_plugins( plugins ):
	for p in plugins:
		try:
			del p
		except:
			raise mesPluginError("WARNING:\tPlugin \"%s\" unloading failed: %s" % (p.name,sys.exc_info()[1]))

def list_from_parser_dict( options ):
	ret = []
	for k,o in options.iteritems():
		if(o['nargs'] == 0):
			if o['value']:
				ret.append( o['option_strings'][0] )
		elif( o['value'] == None or o['value'] == 'None' or o['value'] == '' ):
			if o['required']:
				raise Exception("Encountered a required option without a value: %s" % o['dest'])
		elif(o['nargs'] == None):
			ret.append( o['option_strings'][0] )
			ret.append( str(o['value']) )
		else:
			raise Exception("Encountered an option that could not be converted to a string properly: %s" % o['dest'])
	return ret
		
def setOptionsFromBlock( options, block ):
	for k,o in options.iteritems():

		if(o['nargs'] == 0):
			o['value'] = (o['option_strings'][0] in block['header'][2:])
			continue

		if( not o['option_strings'][0] in block['header'][2:]):
			continue
		else:
			i = block['header'].index(o['option_strings'][0])+1

		if(i > len(block['header'])):
			raise Exception("Header to short to contain a value for key: %s" % o['dest'])
		elif(block['header'][i][0] == o['option_strings'][0][0]):
			raise Exception("Header missing a value for key: %s" % o['dest'])

		if(o['nargs'] == None):
			if(o['type'] == type(0)):
				o['value'] = int( block['header'][i] )
			elif(o['type'] == type(0.0)):
				o['value'] = float( block['header'][i] )
			else:
				o['value'] = block['header'][i]

		else:
			raise Exception("Encountered an option that could not be parsed properly: %s" % o['dest'])
	return options
