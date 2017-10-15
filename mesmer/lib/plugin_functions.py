import sys
import os
import imp
import glob

from exceptions			import *
from setup_functions	import get_installation_dir

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

	# add mesmer package discovery path to the system path
	if getattr(sys, 'frozen', False): # mesmer package already added to sys.modules
		pass 
	else: # add mesmer directory to the system path
		path = os.path.dirname( basedir )
		if not os.path.exists( os.path.join(path,"mesmer") ):
			raise mesPluginError("ERROR:\tCould not find MESMER directory at path \"%s\"." % path)
		sys.path.append( path )

	# add plugin directory to the system path, for plugin-specific libraries
	path = os.path.abspath( os.path.join(basedir, 'plugins') )
	if not os.path.exists( path ):
		raise mesPluginError("ERROR:\tCould not find plugin directory at path \"%s\"." % path)		
	if not path in sys.path:
		sys.path.append( path )

	# some plugins may need access to command line args
	if args is None:
		args = []
	else:
		args = [args]
				
	ret = []
	for f in glob.glob( '%s%s%s_*.py' % (path,os.sep,type) ):

		id, ext = os.path.splitext(os.path.basename(f))
		if id in disabled:
			continue
		
		try:
			file, filename, data = imp.find_module(id, [path])
		except ImportError:
			ret.append( (id, False, "Could not discover plugin at path \"%s\"." % f, None) )
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
