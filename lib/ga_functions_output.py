"""
Contains several useful functions for displaying or saving information/statistics about a MESMER run
"""

import os
import os.path
import operator

from datetime import datetime

from lib.ga_functions_misc import *
from lib.ga_functions_stats import *
from lib.functions import mean_stdv

def print_generation_state( args, ensemble_stats, restraint_stats ):
	
	print_msg( "" )
	print_msg( "\tCurrent time: %s" % datetime.utcnow() )
	print_msg( "\tParent survival percentage: %i%%" % (100*ensemble_stats['ratio']) )
	print_msg( "\n\t\tBest Score\t|\tAverage\t\t|\tStdev" )
	print_msg( "\t\t------------------------------------------------------------" )
	print_msg( "\t\t%.3e\t|\t%.3e\t|\t%.3e" % (
		ensemble_stats['total'][0],
		ensemble_stats['total'][1],
		ensemble_stats['total'][2]) )
	
	target_names = ensemble_stats['target'].keys()

	# print the per-target breakdown of scores	
	for name in target_names:
		if( len(target_names) > 1):
			print_msg( "\n\t%s" % name )
			print_msg( "\tTotal\t%.3e\t|\t%.3e\t|\t%.3e" % (
				ensemble_stats['target'][name][0],
				ensemble_stats['target'][name][1],
				ensemble_stats['target'][name][2]) )

		# print the per-restraint breakdown of scores
		if( len(restraint_stats) > 1):
			for type in restraint_stats:
				print_msg( "\t%s\t%.3e\t|\t%.3e\t|\t%.3e" % (
				type,
				restraint_stats[type][name][0],
				restraint_stats[type][name][1],
				restraint_stats[type][name][2]) )

	print_msg( "" )
	sys.stdout.flush()
	
	return

def print_ensemble_state( args, ratio_stats ):

	print_msg( "" )

	for name in ratio_stats:	
		print_msg( "\t%s" % (name) )
		
		for (c,w,d) in ratio_stats[name]:
			if( args.boots > 0 ):
				print_msg( "\t\t%.3f +/- %.3f\t%s" % (w,d,c) )
			else:
				print_msg( "\t\t%.3f\t%s" % (w,c) )
	
	print_msg( "" )
	sys.stdout.flush()
	
	return

def print_plugin_state( args, counter, plugins, targets, ensembles):
	"""
	foo
	"""
	
	output = []
	for t in targets:
		for r in t.restraints:
			path = os.path.abspath( "%s%srestraints_%s_%s_%05i.out" % (args.dir,os.sep,t.name,r.type,counter) )
	
			for p in plugins:				
				if(r.type in p.type):
					# build the ensemble data list from all ensembles
					all_ensemble_data = []
					for e in ensembles:
						all_ensemble_data.append(e.plugin_data[t.name][r.type])
				
					# retrieve
					(error,messages) = p.ensemble_state(r, t.plugin_data[r.type], all_ensemble_data, path)
					
					if( error != None):
						for m in messages:
							print "Plugin \"%s\" returned an error: %s" % m
							
					break
	
	return True

def write_ensemble_stats( args, counter, targets, ensembles ):
	"""
	Write statistics from the ensemble component ratios to file
	
	Returns: True on success, False on failure
	
	Arguments:
	args		- MESMER argument parameters
	targets		- List of targets
	ensembles	- List of ensembles
	"""
	
	stats = get_ratio_stats( targets, ensembles )

	path = os.path.abspath( "%s%sensemble_statistics_%05i.tbl" % (args.dir,os.sep,counter) )
	
	try:
		f = open( path, 'w' )
	except IOError:
		print "ERROR: Could not write final ratio statistics to file \"%s\"" % (path)
		return False
	
	f.write( "%s\tPrevalence\tAverage\t\tStdev\n" % (''.rjust(32)) )
	
	for t in stats:
		f.write( "\t%s\n" % (t) )

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
			f.write( "%s\t%.1f %%\t\t%.3e\t%.3e\n" % (
				component.rjust(32),
				100*p,
				mean,
				stdev) )
				
		f.write( "" )
	f.close()
	
	return True
	
def write_optimization_state( args, counter, targets, ensembles ):
	
	path = os.path.abspath( "%s%soptimization_state_%05i.tbl" % (args.dir,os.sep,counter) )
	
	try:
		f = open( path, 'w' )
	except IOError:
		print "ERROR: Could not optimization state information to file \"%s\"" % (path)
		return False
	
	for t in targets:
		f.write("\t%s" % (t.name))
	f.write("\n")
	
	for (i,e) in enumerate(ensembles):
		f.write("%i\t" % (i))
		
		a = []
		for t in targets:
			a.append( str(e.opt_status[t.name]) )

		f.write("%s\n" % ("\t".join(a)) )
	
	f.close()
	return	

def write_ensemble_state( args, counter, targets, ensembles ):
	"""
	Write the current state of ensembles (component makeup, per-target ratios and fitnesses) to the MESMER results directory
	
	Returns True on success, or False on failure (e.g. couldn't write to file)
	
	Arguments:
	args		- MESMER argument parameters
	counter		- int, the current generation number
	targets		- list, list of targets
	ensembles	- list, list of ensembles for which to write status
	"""
	
	path = os.path.abspath( "%s%sensembles_%05i.tbl" % (args.dir,os.sep,counter) )
	
	try:
		f = open( path, 'w' )
	except IOError:
		print "ERROR: Could not write ensemble state to file"
		return False
		
	header = []
	str_list = []
	for (i,e) in enumerate(ensembles):

		header.append('#')
		str_list.append( "%05i" % (i) )

		for c in e.component_names:
			header.append('component')
			str_list.append(c)
			
		for t in targets:
			header.append('target')
			str_list.append(t.name)
			header.append('fitness')
			str_list.append( "%.3e" % (sum(e.fitness[t.name].itervalues())) )

			for w in e.ratios[t.name]:
				header.append('ratio')
				str_list.append( "%.3f" % (w) )
				
		header.append("\n")
		
		# write the header only once
		if(i==0):
			f.write("\t".join(header))
		del header[:]
		
		str_list.append("\n")
		
		f.write("\t".join(str_list))
		del str_list[:]
			
	f.close()
	return True
