import sys
import os
import imp
import glob

def load_plugins( args, dir ):
	"""Finds all MESMER plugin (plugin_*.py) files in the provided directory, and loads them"""

	files = glob.glob( '%s/plugin_*.py' % dir )

	plugins = []
	for f in files:
	    plugins.append( load_mesmer_plugin(args, f) )

	return plugins

def load_mesmer_plugin( args, path ):
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

	try:
		module = imp.load_module(name, file, filename, data)
	except:
		print "ERROR: Could not import plugin module \"%s\". Reason: %s" % (name,sys.exc_info()[1])
		return None
	finally:
		file.close()

	try:
		plugin = module.plugin( args )
	except:
		print "ERROR: Could not load plugin \"%s\": %s" % (name,sys.exc_info()[1])
		return None

	# did the user request information about a plugin?
	if (args.plugin == plugin.name) or (args.plugin == name) or (args.plugin in plugin.type):
		plugin.info()
		sys.exit(0)

	return plugin

def unload_plugins( plugins ):
	for p in plugins:
		name = p.name
		try:
			del p
		except:
			print "ERROR: Plugin \"%s\" deletion failed: %s" % (name,sys.exc_info()[1])
			continue
