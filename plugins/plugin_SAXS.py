"""
Creates a MESMER restraint from SAXS data

Target file arguments:
-file <file>	- Read a file containing X Y DY data instead of from the target file
-scale			- Allow scaling of the ensemble profile to better match the target profile
-bg				- Allow the plugin to remove an arbitrary offset to the target data (e.g. poor buffer subtraction or mismatch)
-offset			- Allow a small amount of offset (determine at high q) to better match the target profile
-plot			- Open a plot window showing best fit at each generation

Component file arguments:
-file <file>	- Read a separate file containing X Y data instead of from the component file
"""

import argparse
import os
import shelve
import scipy
import scipy.interpolate as interpolate
import uuid

from StringIO import StringIO

import lib.plugin_tools as tools

name = 'default_SAXS'
version = '2013.05.10'
type = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')

_db_handle = None
_plot_handles = {}

#
# basic functions
#

def load( args ):
	global _db_handle
	
	path ="%s%scomponent_SAXS" % (args.dir,os.sep)
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

def show_best_plot(id,x,y,yfit,diff):

	global _plot_handles
	
	try:
		import matplotlib.pyplot as plot
	except:
		print "Could not load matplotlib!"
		return
	
	plot.ion()
	
	if(not id in _plot_handles.keys()):
		_plot_handles[id] = {}
		_plot_handles[id]['counter'] = 0
		_plot_handles[id]['fig'] = plot.figure()
	
	plot.figure(_plot_handles[id]['fig'].number)
	_plot_handles[id]['fig'].clear()
	_plot_handles[id]['main'] = _plot_handles[id]['fig'].add_axes([0.1,0.1,0.8,0.8])
	plot.title("Best MESMER fit to \"%s\" data" % id)
	plot.yscale('log')
	plot.ylabel('I(q), intensity')
	plot.xlabel(r'$q, \AA^{-1}$')		
	
	_plot_handles[id]['exp'] = plot.plot(x, y, 'ro' )
	_plot_handles[id]['fit'] = plot.plot(x, yfit )

	_plot_handles[id]['inset'] = _plot_handles[id]['fig'].add_axes([0.5,0.5,0.35,0.35])
	plot.title('Residuals')
	plot.yscale('linear')
	plot.ylabel(r'$I(q)_{exp} / I(q)_{fit}$')
	_plot_handles[id]['diff'] = plot.plot(x, diff, 'ro' )
	plot.setp(_plot_handles[id]['inset'], xlim=(0,0.2) )
	
	plot.draw()
	plot.ioff()

	return

def ensemble_state( restraint, target_data , ensembles, file_path):
	"""
	Prints the status of the plugin for the current generation and target
	
	Returns a list of Error_state,output
	
	Arguments:
	target_data		- list of data the plugin has saved for the target
	ensembles	- list of data the plugin has saved for every ensemble in the run, ordered by overall fitness
	filePath		- an optional file path the plugin can save data to
	"""
		
	try:
		f = open( file_path, 'w' )
	except IOError:
		return (False,'Could not open file \"%s\" for writing' % file_path)
	
	f.write("# Best scoring ensemble fit\n" )
	f.write("# scale: %.3e\n" % (ensembles[0]['scale']) )
	f.write("# background offset: %.3e\n" % (ensembles[0]['bg_offset']) )
	f.write("# high-q offset: %.3e\n" % (ensembles[0]['high_q_offset']) )
	f.write("#x\ty_exp\ty_fit\n" )

	# print the fit for the best-scoring ensemble
	y_fit = tools.interpolate_curve( restraint.data['x'], ensembles[0]['x'], ensembles[0]['y'] )
	
	residuals = []
	for (i,x) in enumerate(restraint.data['x']):
		f.write( "%.3f\t%.3f\t%.3f\n" % (x,restraint.data['y'][i],y_fit[i]) )
		
		# calculate the residuals (in this case, the ratio)
		if( y_fit[i] != 0):
			residuals.append( restraint.data['y'][i] / y_fit[i] )
	
	f.close()

	# generate a plot figure if necessary
	if(target_data['args'].plot):
		show_best_plot( restraint.type, restraint.data['x'], restraint.data['y'], y_fit, residuals )
	
	return (None,None)	

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
	parser.add_argument('-file', 	metavar='FILE',			help='The file to read for the SAXS data if not contained in the target file')
	parser.add_argument('-scale', 	action='store_true',	help='Scale the component profiles for a better match to the target profile')
	parser.add_argument('-offset', 	action='store_true',	help='Apply a small offset to improve fit at high q angles')
	parser.add_argument('-bg', 		action='store_true',	help='Perform background subtraction to better match the target profile.')
	parser.add_argument('-plot', 	action='store_true',	help='Create a plot window at each generation showing fit to data')

	try:
		args = parser.parse_args(block['header'].split()[2:])
	except argparse.ArgumentError, exc:
		return (False,["Argument error: %s" % exc.message()])
		
	target_data['args'] = args

	# attempt to load the SAXS profile			
	if(args.file == None):
		try:
			values = scipy.genfromtxt( StringIO( ''.join(block['content'])) )
		except ValueError, exc:
			return (False,["Could not parse SAXS data in target file - %s " % (exc)])
	else:
		try:
			values = scipy.genfromtxt(args.file)
		except ValueError, exc:
			return (False,["Could not read file \"%s\" - %s" % (args.file, exc)])
			
	if(len(values[0]) != 3):
		return (False,["Target SAXS data must be of the format: x y dy"])
	
	restraint.data['x'] = zip(*values)[0]
	restraint.data['y'] = zip(*values)[1]
	restraint.data['d'] = zip(*values)[2]

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
	parser.add_argument('-file', metavar='FILE', help='The file to read for the SAXS data if not contained in the target file')

	try:
		args = parser.parse_args(block['header'].split()[1:])
	except argparse.ArgumentError, exc:
		return (False,["Argument error: %s" % exc.message()])

	if(args.file == None):
		try:
			values = scipy.genfromtxt( StringIO( ''.join(block['content'])) )
		except ValueError, exc:
			return (False,["Could not parse SAXS data in component file - %s" % (exc)])
	else:
		try:
			values = scipy.genfromtxt(args.file)
		except ValueError, exc:
			return (False,["Could not read file \"%s\" - %s" % (args.file, exc)])

	if(len(values[0]) != 2):
		return (False,["Component SAXS data must be of the format: x y"])

	# attempt to interpolate the XY values against the target restraint X values
	try:
		temp = interpolate.splrep( zip(*values)[0], zip(*values)[1] )
		interpolate.splev( attribute.restraint.data['x'],temp )
	except TypeError:
		return (False,["Could not interpolate the component's SAXS curve to the target's"])

	# generate a unique key for storing the attribute value into the db
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
	
	bootstrap.data['x'] = restraint.data['x']
	bootstrap.data['y'] = tools.make_interpolated_bootstrap_sample( restraint.data['x'], restraint.data['y'], ensemble_data['x'], ensemble_data['y'] )
	bootstrap.data['d'] = restraint.data['d']
		
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

	n = len(restraint.data['x'])
	
	# average the attribute profiles
	fit = tools.make_weighted_vector( [interpolate.splev(restraint.data['x'], _db_handle[a.data['key']]) for a in attributes], ratios )
	
	# determine the scaling and/or offset coefficients
	if(target_data['args'].scale and target_data['args'].bg):
		(ensemble_data['scale'],ensemble_data['bg_offset']) = tools.get_curve_transforms( list(restraint.data['y']) , restraint.data['d'], fit[:] )
	elif(target_data['args'].scale):
		ensemble_data['scale'] = tools.get_scale( restraint.data['y'], restraint.data['d'], fit[:] )
		ensemble_data['bg_offset'] = 0.0
	elif(target_data['args'].bg):
		ensemble_data['scale'] = 1.0
		ensemble_data['bg_offset'] = tools.get_offset( restraint.data['y'], fit[:] )
	else:
		ensemble_data['scale'] = 1.0
		ensemble_data['bg_offset'] = 0.0
			
	# apply the scaling and offset coefficients to the dataset
	for i in range(n):
		fit[i] = (fit[i] * ensemble_data['scale']) + ensemble_data['bg_offset']

	# determine high-q offset
	if(target_data['args'].offset):
		ensemble_data['high_q_offset'] = tools.get_offset( restraint.data['y'], fit, -0.750 )

		for i in range(n):
			fit[i] += ensemble_data['high_q_offset']
	else:
		ensemble_data['high_q_offset'] = 0.0
	
	# Save all of these parameters to the ensemble_data object for future retrieval
	ensemble_data['x'] = restraint.data['x']
	ensemble_data['y'] = fit
	
	return tools.get_chisq_reduced( restraint.data['y'], restraint.data['d'], fit )

	