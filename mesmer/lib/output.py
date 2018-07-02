import os
import os.path
import operator
import shelve

from mesmer.errors import *
from mesmer.lib.statistics import *

_MESMER_ENSEMBLES_FILE_FORMAT	= 'ensembles_%s_%05i.tbl'
_MESMER_STATISTICS_FILE_FORMAT	= 'component_statistics_%s_%05i.tbl'
_MESMER_CORRELATION_FILE_FORMAT	= 'component_correlations_%05i.tbl'
_MESMER_RESTRAINTS_FILE_FORMAT	= 'restraints_%s_%s_%05i.out'
_MESMER_OPT_STATUS_FILE_FORMAT	= 'optimization_state_%s_%05i.tbl'

def log_generation_state( logger, args, counter, ensemble_stats, restraint_stats ):
	"""
	Print the status of the current generation via print_msg()

	Args:
		args (argparse namespace): MESMER argument parameters
		ensemble_stats (dict): A complex dictionary containing ensemble statistics. See get_best_ensembles() for more info.
		restraint_stats (dict): A complex dictionary containing restraint statistics. See get_restraint_stats() for more info.

	Returns: None
	"""

	logger.info( "\tParent survival percentage: %i%%, %i unique ensembles" % (100*ensemble_stats['ratio'],ensemble_stats['unique']) )
	logger.info( "\t\tBest Score\t|\tAverage\t\t|\tStdev" )
	logger.info( "\t\t------------------------------------------------------------" )
	logger.info( "\t\t%.3e\t|\t%.3e\t|\t%.3e" % (
		ensemble_stats['total'][0],
		ensemble_stats['total'][1],
		ensemble_stats['total'][2]) )

	target_names = ensemble_stats['target'].keys()

	# print the per-target breakdown of scores
	for name in target_names:
		if( len(target_names) > 1):
			logger.info( "\n\t%s" % name )
			logger.info( "\tTotal\t%.3e\t|\t%.3e\t|\t%.3e" % (
				ensemble_stats['target'][name][0],
				ensemble_stats['target'][name][1],
				ensemble_stats['target'][name][2]) )

		# print the per-restraint breakdown of scores
		if( len(restraint_stats) > 1):
			for type in sorted(restraint_stats.keys()):
				logger.info( "\t%s\t%.3e\t|\t%.3e\t|\t%.3e" % (
				type,
				restraint_stats[type][name][0],
				restraint_stats[type][name][1],
				restraint_stats[type][name][2]) )

	# write to MESMER results db
	if logger.db is None:
		logger.Warn( "Tried to log generation state, but no logging database is present.")
		return

	if 'ensemble_stats' not in logger.db.keys():
		logger.db['ensemble_stats'], logger.db['restraint_stats'] = [], []
	
	a, b = logger.db['ensemble_stats'], logger.db['restraint_stats']

	# large numbers of ensemble scores makes depickling run *extremely* slow, so no ensemble_stats['ratios']
	a.append( (ensemble_stats['total'],ensemble_stats['ratio'],ensemble_stats['target']) )
	b.append(restraint_stats)

	logger.db['ensemble_stats'], logger.db['restraint_stats'] = a, b

	return

def log_ensemble_state( logger, args, ratio_stats ):
	"""
	Print the components of an ensemble via print_msg()

	Args:
		args (argparse namespace): MESMER argument parameters
		ratio_stats (dict): A dictionary keyed by component names containing a three-component tuple: best weight, average weight, and (optionally) weight stdev
	
	Returns: None
	"""

	for name in ratio_stats:
		logger.info( "\t%s" % (name) )

		for (c,w,d) in ratio_stats[name]:
			if( args.boots > 0 ):
				logger.info( "\t\t%.3f +/- %.3f\t%s" % (w,d,c) )
			else:
				logger.info( "\t\t%.3f\t%s" % (w,c) )

	return

def log_plugin_state( logger, args, counter, plugins, targets, ensembles):
	"""
	Call the ensemble_state function for each plugin if the argument -Pstate is set
	
	This function is called at each generation, and gives plugins a chance to print statistics or other aggregate information
	
	Args:
		counter (int): Generation counter used to build output path
		plugins	(list): List of Plugins
		targets	(list): List of Targets
		ensembles (list): List of mesEnsembles
		
	Returns: True on success, False on failure. Errors from plugins are reported via the logger.
	"""

	if logger.fp is None:
		logger.Error( "Tried to log plugin states, but no output directory for logger is present.")
		return False

	output = []
	for t in targets:
		for r in t.restraints:
			path = os.path.join(
				os.path.dirname(logger.fp),
				_MESMER_RESTRAINTS_FILE_FORMAT%(t.name,r.type,counter))

			for p in plugins:
				if(r.type in p.types):
					# build the ensemble data list from all ensembles
					all_ensemble_data = []
					for e in ensembles:
						all_ensemble_data.append(e.plugin_data[t.name][r.type])

					try:
						messages = p.ensemble_state(r, t.plugin_data[r.type], all_ensemble_data, path)
					except mesPluginError as e:
						logger.Error("Plugin \"%s\" returned an error: %s" % e.msg)

					break

	return True

def write_component_stats( logger, args, counter, ensembles ):
	"""
	Write component correlations from the provided ensembles to file

	Args:
		args (argparse namespace): MESMER argument parameters
		counter (int): Generation counter (used to build file path)
		ensembles (list): List of mesEnsembles
	
	Returns: True on success, False on failure
	"""

	if logger.fp is None:
		logger.Error( "Tried to log component stats, but no output directory for logger is present.")
		return False

	(names,relative,absolute) = get_component_correlations( args, ensembles )
	n = len(names)

	# don't bother printing an empty table
	if(n==0):
		return True

	path = os.path.join(
		os.path.dirname(logger.fp),
		_MESMER_CORRELATION_FILE_FORMAT%(counter))

	try:
		f = open( path, 'w' )
	except IOError:
		logger.Error( "Could not write component correlation table to file \"%s\"" % (path) )
		return False

	# print table header
	for name in names:
		f.write("\t%s" % name,)
	f.write("\n")

	toggle = 0
	for i in range(n):
		f.write("%s\t" % names[i])

		for j in range(n):

			# toggle from absolute to relative correlation
			if( i == j ):
				toggle = 1

			if(toggle > 0):
				f.write("%0.3f\t" % relative[i][j])
			else:
				f.write("%0.3f\t" % absolute[i][j])

		f.write("\n")
		toggle = 0

	f.close()

	return True

def write_ensemble_stats( logger, args, counter, targets, ensembles ):
	"""
	Write statistics from the ensemble component ratios to file

	Args:
		args (argparse namespace): MESMER argument parameters
		targets	(list): List of mesTargets
		ensembles (list): List of mesEnsembles

	Returns: True on success, False on failure
	"""

	if logger.fp is None:
		logger.Error( "Tried to log component stats, but no output directory for logger is present.")
		return False

	stats = get_ratio_stats( targets, ensembles )

	# go through each target
	for t in stats:

		path = os.path.join(
			os.path.dirname(logger.fp),
			_MESMER_STATISTICS_FILE_FORMAT%(t,counter))

		try:
			f = open( path, 'w' )
		except IOError:
			logger.error( "Could not write ensemble statistics to file \"%s\"" % (path) )
			return False

		f.write( "%s\tPrevalence\tAverage\t\tStdev\n" % (''.rjust(32)) )

		# order components by prevalence
		component_counts = []
		for component in stats[t]:
			component_counts.append( (component,len(stats[t][component])) )
		component_counts.sort( key=operator.itemgetter(1), reverse=True )

		for (component,count) in component_counts:
			p = float(count)/args.ensembles
			# don't show stats for components with low prevalence
			if( p*100 < args.Pmin):
				break

			(mean,stdev) = mean_stdv( stats[t][component] )
			f.write( "%s\t%.3f %%\t\t%.3e\t%.3e\n" % (
				component.rjust(32),
				100*p,
				mean,
				stdev) )

		f.write( "" )
	f.close()

	return True

def write_optimization_state( logger, counter, targets, ensembles ):
	"""
	Writes the optimizations state for each ensemble to a file

	Args:
		counter (int):Generation counter used to build the file output path
		targets (list): List of mesTargets
		ensembles (list): List of mesEnsembles

	Returns: True on success, False on failure (also prints an error message to stdout)
	"""

	if logger.fp is None:
		logger.error( "Tried to log ensemble optimization states, but no output directory for logger is present.")
		return False

	for t in targets:

		path = os.path.join(
			os.path.dirname(logger.fp),
			_MESMER_OPT_STATUS_FILE_FORMAT%(t.name,counter))

		try:
			f = open( path, 'w' )
		except IOError:
			logger.error( "Could not optimization state information to file \"%s\"" % (path) )
			return False

		for (i,e) in enumerate(ensembles):
			f.write("%i\t" % (i))

			a = []
			for t in targets:
				a.append( str(e.opt_status[t.name]) )

			f.write("%s\n" % ("\t".join(a)) )

	f.close()
	return True

def write_ensemble_state( logger, args, counter, targets, ensembles ):
	"""
	Write the current state of ensembles (component makeup, per-target ratios and fitnesses) to the MESMER results directory

	Args:
		counter (int): The current generation number
		targets (list): List of Targets
		ensembles (list): List of Ensembles for which to write status
		
	Returns: True on success, or False on failure (e.g. couldn't write to file) @TODO@: Maybe raise an exception instead?
	"""
	if logger.fp is None:
		logger.error( "Tried to log ensemble states, but no output directory for logger is present.")
		return False

	for t in targets:

		path = os.path.join(
			os.path.dirname(logger.fp),
			_MESMER_ENSEMBLES_FILE_FORMAT%(t.name,counter))

		try:
			f = open( path, 'w' )
		except IOError:
			logger.error( "Could not write ensemble state to file \"%s\" " % (path) )
			return False

		str_list = ['#']
		for i in range(len(ensembles[0].component_names)):
			str_list.append('component')

		str_list.append('fitness')

		for i in range(len(ensembles[0].component_names)):
			str_list.append('ratio')

		str_list.append("\n")

		f.write("\t".join(str_list))
		del str_list[:]

		for (i,e) in enumerate(ensembles):
			str_list.append( "%05i" % (i) )

			for c in e.component_names:
				str_list.append(c)

			str_list.append( "%.3e" % (sum(e.fitness[t.name].itervalues())) )

			for w in e.ratios[t.name]:
				str_list.append( "%.3f" % (w) )

			str_list.append("\n")

			f.write("\t".join(str_list))
			del str_list[:]

		f.close()

	return True
