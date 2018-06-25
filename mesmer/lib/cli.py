import sys

from lib						import __version__,__author__
from lib.exceptions				import *
from lib.setup_functions		import *
from lib.utility_functions		import print_msg
from lib.plugin_functions		import load_plugins,unload_plugins
from lib.target_functions		import load_targets
from lib.component_functions	import load_components
from lib.ga_functions_main		import run_ga

def run():
	print("-"*40)
	print("MESMER v. %s \n(c) %s" % (__version__,__author__))
	print("-"*40+"\n")

	if( sys.version_info < (2,6) ):
		print "ERROR:\tPython version must be 2.6 or greater"
		sys.exit(1)

	# setup sys.path for plugins
	try:
		mesmer_path = set_module_paths()
	except mesSetupError as e:
		print e.msg
		sys.exit(1)

	# get mesmer user preferences
	try:
		prefs = open_user_prefs(mode='c')
	except mesSetupError as e:
		print "ERROR:\tCannot read or create MESMER preferences file: %s"%(e)
		sys.exit(1)
			
	# obtain the parameters for the run
	args = parse_arguments(prefs=prefs)
	
	# attempt to load available plugin modules
	plugins = []
	try:
		for id,ok,msg,module in load_plugins(mesmer_path, 'mesmer', args=args ):
			if ok:
				plugins.append( module )
			else:
				print("WARNING:\tPlugin \"%s\" failed to load: (%s)."%(id,msg))			
	except mesPluginError as e:
		print "%s\nPerhaps the MESMER preferences are misconfigured?"%(e)
		
	# did the user request information about a plugin?
	for p in plugins:
		if (args.plugin == p.name) or (args.plugin in p.types):
			print str(p)
			sys.exit(0)

	if len(plugins) == 0:
		raise mesPluginError("ERROR:\tNo valid MESMER interpreter plugins found.")
		sys.exit(1)
		
	# attempt to create the fitting results directory
	try:
		make_results_dir(args)
	except mesSetupError as e:
		print e.msg
		sys.exit(1)

	# print information about the MESMER environment to the log file
	print_msg("\nPlugins:")
	for p in plugins:
		print_msg("\t%s\t:\t%s"%(p.name,p.version))

	# save the parameters list to the log file
	print_msg("\nArguments:")
	for k in vars(args):
		print_msg("\t%s\t:\t%s" % (k,vars(args)[k]))
	print_msg("")

	# load target restraints by passing off to plugins
	try:
		targets = load_targets( args, plugins )
	except mesTargetError as e:
		print e.msg
		sys.exit(1)

	# create component database
	try:
		components = load_components( args, plugins, targets )
	except mesComponentError as e:
		print e.msg
		sys.exit(1)

	# Start the algorithm
	ret = run_ga( args, plugins, targets, components )

	# finished, unload plugins
	try:
		unload_plugins( plugins )
	except mesPluginError as e:
		print e.msg
		sys.exit(1)
