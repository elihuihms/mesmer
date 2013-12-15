import sys
import os
import imp
import glob

from exceptions import *

def load_plugins( dir, type, *args ):
	"""
	Finds all MESMER plugin (plugin_*.py) files in the provided directory, and returns them
	"""

	plugins = []
	for f in glob.glob( '%s%splugins%s%s_*.py' % (dir,os.sep,os.sep,type) ):

		name, ext = os.path.splitext(os.path.basename(f))
		try:
			file, filename, data = imp.find_module(name, [os.path.join(dir,'plugins')])
		except ImportError:
			raise mesPluginError("ERROR: Could not discover plugin at path \"%s\"." % f)

		try:
			module = imp.load_module(name, file, filename, data)
		except:
			raise mesPluginError("ERROR: Could not import plugin module \"%s\". Reason: %s" % (name,sys.exc_info()[1]))
		finally:
			file.close()

		# following is not exception-wrapped for easier debugging in MESMER
		plugins.append( module.plugin( *args ) )

	return plugins

def unload_plugins( plugins ):
	for p in plugins:
		try:
			del p
		except:
			raise mesPluginError("ERROR: Plugin \"%s\" unloading failed: %s" % (p.name,sys.exc_info()[1]))
