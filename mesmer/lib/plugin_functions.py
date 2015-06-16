import sys
import os
import imp
import glob

from exceptions import *

def load_plugins( dir, type, dry_run=False, disabled=[], args=None ):
	"""
	Finds all MESMER plugin (plugin_*.py) files in the provided directory, and returns them
	"""

	# add lib directory to the system path
	path = os.path.abspath( dir )
	if not path in sys.path:
		sys.path.append( path )

	# add plugin directory to the system path, for plugin-specific libraries
	path = os.path.abspath( os.path.join(dir, 'plugins') )
	if not os.path.exists( path ):
		raise mesPluginError("ERROR: Could not find plugin directory at path \"%s\"." % path)
	
	if not path in sys.path:
		sys.path.append( path )
	
	# some plugins may need access to command line args
	if args is None:
		args = []
	else:
		args = [args]
				
	plugins = []
	for f in glob.glob( '%s%s%s_*.py' % (path,os.sep,type) ):

		id, ext = os.path.splitext(os.path.basename(f))
		if id in disabled:
			continue
		
		try:
			file, filename, data = imp.find_module(id, [path])
		except ImportError:
			if dry_run:
				plugins.append( (id, False, "Could not discover plugin at path \"%s\"." % f, None) )
				continue
			else:
				raise mesPluginError("ERROR: Could not discover plugin at path \"%s\"." % f)

		try:
			module = imp.load_module(id, file, filename, data)
		except:
			if dry_run:
				plugins.append( (id, False, "Could not import plugin module \"%s\". Reason: %s" % (id,sys.exc_info()[1]), None) )
				continue
			else:
				raise mesPluginError("ERROR: Could not import plugin module \"%s\". Reason: %s" % (id,sys.exc_info()[1]))
		finally:
			file.close()

		if dry_run:
			try:
				plugins.append( (id, True, '', module.plugin( *args )) )
			except:
				plugins.append( (id, False, "Could not load plugin \"%s\". Reason: %s" % (id,sys.exc_info()[1]), None) )
				
		else:
			# following is not exception-wrapped for easier debugging
			plugins.append( module.plugin( *args ) )

	return plugins

def unload_plugins( plugins ):
	for p in plugins:
		try:
			del p
		except:
			raise mesPluginError("ERROR: Plugin \"%s\" unloading failed: %s" % (p.name,sys.exc_info()[1]))
