"""
Creates a MESMER restraint from a general list of data

Target file arguments:
-file <file>	- Read a file containing whitespace-delimited data instead of from the target file
-col <n>		- The column of values in the list to use

Component file arguments:
-file <file>	- Read a file containing whitespace-delimited data instead of from the target file
"""

import shelve
import argparse
import math
import os
import sys
import scipy
import scipy.interpolate as interpolate
import uuid

from StringIO import StringIO

import lib.plugin_tools as tools

name = 'default_LIST'
version = '2013.xx.xx'
type = ('LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9')

_db_handle = None
_ensemble_plot_handle = None

#
# basic functions
#

def load( args ):
	global _db_handle
	
	path ="%s%scomponent_LIST.db" % (args.dir,os.sep)
	try:
		_db_handle = shelve.open(path,'c')
	except:
		return "Could not create temporary DB."

	return None
		
def unload():
	global _db_handle
	if (_db_handle != None):
		_db_handle.close()
	
	return None

def info():
	global name
	global version
	global types
	print "Plugin: \"%s\"" % name
	print "\tversion: \"%s\"" % version
	print "\tdata types:"
	for t in types:
		print "\t\t%s" % t

#
# output functions
#

def ensemble_state( restraint, target_data, ensembles, file_path):
	"""
	Prints the status of the plugin for the current generation and target
	
	Returns a list of Error_state,output
	
	Arguments:
	target_data		- list of data the plugin has saved for the target
	ensemble_data	- list of data the plugin has saved for every ensemble in the run, ordered by overall fitness
	filePath		- an optional file path the plugin can save data to
	"""
	
	try:
		f = open( file_path, 'w' )
	except IOError:
		return (False,'Could not open file \"%s\" for writing' % file_path)
	
	f.write("# (identifiers)\texp\tfit\tres")
	for key in ensembles[0]['values']:
		tmp = key.replace('.',"\t")
		res = restraint.data['values'][key] - ensembles[0]['values'][key]
		f.write("%s\t%f\t%f\t%f\n" % (tmp,restraint.data['values'][key],ensembles[0]['values'][key],res) )
	
	f.close()
	
	return (None,[])	

#
# data handling functions
#

def load_restraint( restraint, block, target_data ):
	"""
	Initializes the provided restraint with information from the target file
	
	Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).
	
	Arguments:
	target_data	- The plugin's data storage variable for the target
	block		- The block dict provided by MESMER (see the mesRestraint docstring for more information)
	restraint	- The empty restraint object to be filled
	"""
	global name
	messages = []
	
	parser = argparse.ArgumentParser(prog=name,usage='See plugin documentation for parameters')
	parser.add_argument('-file', 	action='store',								help='An external whitespace-delimited file containing LIST parameters.')
	parser.add_argument('-col', 	action='store',	type=int,	required=True,	help='The column of data to use as the restraint')

	try:
		args = parser.parse_args(block['header'].split()[2:])
	except argparse.ArgumentError, exc:
		return (False,["Argument error: %s" % exc.message()])
		
	restraint.data['args'] = args
	
	if(args.file):
		try:
			f = open(args.file)
			table = f.readlines()
			f.close()
		except:
			return(False,["Error reading from file \"%s\": " % (file,sys.exc_info()[1])])
	else:
		table = block['content']
	
	data = []
	for line in table:
		line = line.strip()
		data.append( [field.strip() for field in line.split()] )
	
	restraint.data['values'] = {}
	for e in data:
		if( len(e) >= args.col ):
			key = '.'.join( e[:args.col] )
			restraint.data['values'][key] = float(e[args.col])
			
	return (True,messages)

def load_attribute( attribute, block, ensemble_data ):
	"""
	Initializes the provided attribute with information from a component file
	
	Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).
	
	Arguments:
	ensemble_data	- The plugin's data storage variable for this ensemble
	block			- The block dict provided by MESMER
	attribute		- The empty attribute object to be filled
	"""
	global name
	global _db_handle
	
	messages = []
	
	parser = argparse.ArgumentParser(prog=name,usage='See plugin documentation for parameters')
	parser.add_argument('-file', 	action='store',								help='An external whitespace-delimited file containing LIST parameters.')

	try:
		args = parser.parse_args(block['header'].split()[1:])
	except argparse.ArgumentError, exc:
		return (False,["Argument error: %s" % exc.message()])

	if(args.file):
		try:
			f = open(args.file)
			table = f.readlines()
			f.close()
		except:
			return(False,["Error reading from file \"%s\": " % (file,sys.exc_info()[1])])
	else:
		table = block['content']
		
	data = []
	for line in table:
		line = line.strip()
		data.append( [field.strip() for field in line.split()] )

	col = attribute.restraint.data['args'].col
	
	temp = {}
	for e in data:
		key = '.'.join( e[:col] )
		if( key in attribute.restraint.data['values'].keys() ):
			temp[key] = float(e[col])

	# generate a unique key for storing the attribute table into the db
	attribute.data['key'] = uuid.uuid1().hex

	# store the spline into the database
	_db_handle[attribute.data['key']] = temp
	
	return (True,messages)

def load_bootstrap( bootstrap, restraint, ensemble_data, target_data ):
	"""
	Generates a bootstrap restraint using the provided ensemble data
	
	Arguments:
	bootstrap		- mesRestraint, the restraint to fill with the bootstrap sample
	restraint		- mesRestraint, the restraint serving as the template for the sample
	ensemble_data	- The plugin's data storage variable for this ensemble
	target_data		- The plugin's data storage variable for the target
	"""
	
	n = len(ensemble_data['values'])
	exp = [0.0]*n
	fit = [0.0]*n
	for (i,key) in enumerate(ensemble_data['values'].keys()):
		exp[i] = restraint.data['values'][key]	
		fit[i] = ensemble_data['values'][key]

	tmp = tools.make_bootstrap_sample( exp, fit )
	bootstrap.data['values'] = ensemble_data['values']
	
	# docs say that if the ensemble dict is not modified, iteration order will be unchanged!
	for (i,key) in enumerate(ensemble_data['values'].keys()):
		bootstrap.data['values'][key] = tmp[i]
	
	return (True,[])

def calc_fitness( restraint, target_data, ensemble_data, attributes, ratios ):
	"""
	Calculates the fitness of a set of attributes against a given restraint
	
	Returns a fitness score, which is actually the reduced chi-squared goodness-of-fit value between the restraint SAXS profile and the weighted-sum component SAXS profiles (attributes)
	
	Arguments:
	ensemble_data	- The plugin's data storage variable for the ensemble
	restraint		- The restraint object to be fitted against
	attrbutes		- A list of attributes to be averaged together and compared to the restraint
	ratios			- The relative weighting (ratio) of each attribute
	"""
	
	global _db_handle
	
	assert(len(attributes) == len(ratios))
	
	if(not 'values' in ensemble_data.keys()):
		ensemble_data['values'] = {}

	n = len(restraint.data['values'])
	exp_rms = 0.0
	diffs = [0.0]*n
	for (i,key) in enumerate(restraint.data['values']):
		
		exp_rms += (restraint.data['values'][key])**2
		avg = 0.0
		for (j,a) in enumerate(attributes):
			avg += ratios[j] * _db_handle[ a.data['key'] ][key]
		
		diffs[i] = restraint.data['values'][key] - avg
		ensemble_data['values'][key] = avg
		
	return tools.get_rms(diffs) / math.sqrt(exp_rms/n)
	