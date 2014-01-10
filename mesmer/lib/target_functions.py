from exceptions			import *
from utility_functions	import print_msg
from target_objects		import mesTarget,mesTargetError

def load_targets( args, plugins ):
	"""
	Loads all targets specified in the args by passing them off to the appropriate plugins
	"""

	if(len(args.target) < 0):
		raise mesTargetError("ERROR: No targets specified.")

	names, targets = [], []

	for f in args.target:
		print_msg("INFO: Reading target file \"%s\"" % (f))

		targets.append( mesTarget() )

		if( not targets[-1].load(f,plugins) ):
			raise mesTargetError("ERROR: Could not load target file \"%s\"." % (f))

		if( targets[-1].name in names ):
			raise mesTargetError("ERROR: Target file \"%s\" has the same name (%s) as a previous target." % (f,targets[-1].name))

		names.append(targets[-1].name)

	for t in targets:
		if( len(targets[0].restraints) != len(t.restraints) ):
			raise mesTargetError("ERROR: All targets in titration analysis must have the same number of restraints.")

	return targets