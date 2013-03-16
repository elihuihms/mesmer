import sys
import os
import imp
import glob

def load_plugins( dir ):
	"""Finds all MESMER plugin (plugin_*.py) files in the provided directory, and loads them"""
	
	files = glob.glob( '%s/plugin_*.py' % dir )
	
	plugins = []
	for f in files:
	    plugins.append( load_mesmer_plugin(f) )
	
	return plugins

def load_mesmer_plugin( path ):
	"""
	Import the python module at the specified path.
	
	Returns the result of imp.load_module() on success. If the module can't be found via imp.find_module, returns None and prints an error to stdout.
	"""
	
	dir, base = os.path.split(path)
	name, ext = os.path.splitext(base)
	
	try:
		file, filename, data = imp.find_module(name, [dir])
	except ImportError:
		print "ERROR: Could not discover plugin at path \"%s\"." % (path)
		return None
	
	plugin = imp.load_module(name, file, filename, data)
	file.close()
	
	#try:
	#	plugin = imp.load_module(name, file, filename, data)
	#except:
	#	print "ERROR: Could not import plugin \"%s\". Reason: %s" % (name,sys.exc_info()[1])
	#	return None
	#finally:
	#	file.close()
		
	return plugin
	
#
# UNUSED FUNCTIONS BELOW THIS LINE
#

def testPlugin( plugin ):
	"""
	Runs basic sanity checks to assess the validity of the passed plugin, returns False on failure, otherwise True
	"""
	
	try:
		plugin = module.handler()
	except:
		print "ERROR: Could not import module \"%s\". Reason: %s" % (name,sys.exc_info()[1])
		return None
	finally:
		file.close()

	try:
		plugin.load()
	except:
		print "ERROR: Plugin module \"%s\" could not be loaded. Reason: %s" % (name,sys.exc_info()[1])
		return None

	if( testPlugin(plugin) ):
		return plugin
	else:
		print "ERROR: Plugin module \"%s\" did not pass sanity checks." % (name)
		return None
	
	try:
		assert( plugin.name != None )
	except:
		print "ERROR: Last loaded plugin is not named."
		return False
	
	try:
		assert( plugin.type != None )
	except:
		print "ERROR: Plugin \"%s\" does not possess an valid type list." % (name)
		return False
		
	try:
		assert( plugin.errors != None )
	except:
		print "ERROR: Plugin \"%s\" does not possess an error log." % (name)
		return False
	
	try:
		plugin.restraint( {'type':'TEST', 'header':'TEST','content':[], 'l_start':0,'l_end':0} )
	except NameError:
		print "ERROR: Plugin \"%s\" could not make a restraint." % (name)
		return False
	
	return True
		