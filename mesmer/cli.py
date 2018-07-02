import sys

from mesmer import __version__,__author__
from mesmer.errors import *
from mesmer.setup import *
from mesmer.lib import *
from mesmer.output import *

def run(args=None):
	log = Logger()

	args = parse_arguments(args)
	path = open_results_dir( log, args )

	if path is None:
		log.shutdown()
		sys.exit(1)

	log.info("-"*40)
	log.info("MESMER v. %s" % (__version__))
	log.info("(c) %s" % (__author__))
	log.info("-"*40)

	try: # setup sys.path for plugins
		set_module_paths()
	except mesSetupError as e:
		log.exception( e.msg )
		log.shutdown()
		sys.exit(1)

	try:
		opt = Optimizer( log, args )
	except mesError as e:
		log.error( "Could not initialize genetic algorithm: %s"%(e) )
		log.shutdown()
		sys.exit(1)

	for p in opt.plugins:
		if (args.plugin == p.name) or (args.plugin in p.types):
			log.info(str(p))
			log.shutdown()
			sys.exit(0)

	log.info("Plugins:")
	for p in opt.plugins:
		log.info("%s\t:\t%s"%(p.name,p.version))

	log.info("Arguments:")
	for k in vars(args):
		log.info("%s\t:\t%s" % (k,vars(args)[k]))

	try:
		opt.run()
	except mesError as e:
		log.error( "Failed during optimization: %s"%(e))
		log.shutdown()
		sys.exit(1)

	log.shutdown()
	sys.exit(0)
