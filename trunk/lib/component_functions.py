import os
import sys
import tempfile
import glob
import tarfile
import shelve

from exceptions			import *
from utility_functions	import print_msg
from component_objects	import mesComponent,mesComponentError

def load_components( args, plugins, targets ):

	files = []
	for f in args.components:

		if( os.path.isdir(f[0]) ):
			files.extend( glob.glob( "%s%s*" % (f[0],os.sep) ) )
		elif( os.path.isfile(f[0]) ):
			files.extend( f[0] )
		else:
			raise mesComponentError("ERROR: Specified component or directory \"%s\" does not exist" % f[0])

	if(len(files) == 0):
		raise mesComponentError("ERROR: No components specified.")

	print_msg("INFO: Found %i component files." % (len(files)))
	components = {}

	names = [''] * len(files)
	divisor = int(max(len(files)/100,1))
	for (i,f) in enumerate(files):
		if( i % divisor == 0 ):
			sys.stdout.write("Component loading progress: %i%%\r" % (100.*i/len(files)+1) )
			sys.stdout.flush()

		temp = mesComponent()

		if( not temp.load(f,plugins,targets) ):
			raise mesComponentError("\nERROR: Could not load component file \"%s\"." % (f))

		if( temp.name in names ):
			raise mesComponentError("\nERROR: Component file \"%s\" has the same NAME as a previous component." % (f))

		# add the component to the component database
		components[temp.name] = temp
		names[i] = temp.name

	sys.stdout.write("\n")

	return components