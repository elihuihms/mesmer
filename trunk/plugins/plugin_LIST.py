"""
Creates a MESMER restraint from a general list of data (NOEs, Pseudocontact shifts, etc.)

Target file arguments:
-file <file>	- Read a separate file containing whitespace-delimited data instead of the target file
-col <n>		- The column of values in the list to use
-sse			- Report fitness as a sum square of error
-harm			- Report fitness as sum deviation from a flat-bottomed harmonic potential for each term (intervals should be provided in -col N+1 column)
-Q				- Report fitness as a quality (Q) factor, normalized against the RMS of the experimental data

Component file arguments:
-file <file>	- Read a file containing whitespace-delimited data instead of from the target file
"""

import argparse
import sys

from scipy import interpolate
from numpy import sqrt,mean

from lib.plugin_primitives import plugin_db
import lib.plugin_tools as tools

class plugin( plugin_db ):
	name = 'default_LIST'
	version = '2013.07.19'
	type = ('LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9')

	_plot_handles = {}

	#
	# custom functions
	#

	def showplot( self, id, exp, fit ):

		try:
			import matplotlib.pyplot as plot
		except:
			print "Could not load matplotlib!"
			return

		plot.ion()

		if(not id in self._plot_handles.keys()):
			self._plot_handles[id] = {}
			self._plot_handles[id]['fig'] = plot.figure()

		plot.figure(self._plot_handles[id]['fig'].number)
		self._plot_handles[id]['fig'].clear()
		self._plot_handles[id]['main'] = self._plot_handles[id]['fig'].add_axes([0.1,0.1,0.8,0.8])
		plot.title("Best MESMER fit to \"%s\" data" % id)
		plot.ylabel('Fit Value')
		plot.xlabel('Experimental Value')

		self._plot_handles['exp'] = plot.plot(exp, fit, 'ro' )

		plot.draw()
		plot.ioff()

		return

	#
	# output functions
	#

	def ensemble_state( self, restraint, target_data, ensemble_data, file_path):
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
			return (False,['Could not open file \"%s\" for writing' % file_path])

		f.write("# (identifiers)\texp\tfit\n")
		for i in range(len(restraint.data['x'])):
			tmp = restraint.data['x'][i].replace('.',"\t")
			f.write("%s\t%.3E\t%.3E\n" % (tmp,restraint.data['y'][i],ensemble_data[0]['y'][i]) )
		f.close()

		if(restraint.data['args'].plot):
			self.showplot( restraint.type, restraint.data['y'], ensemble_data[0]['y'] )

		return (True,[])

	#
	# data handling functions
	#

	def load_restraint( self, restraint, block, target_data ):
		"""
		Initializes the provided restraint with information from the target file

		Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).

		Arguments:
		target_data	- The plugin's data storage variable for the target
		block		- The block dict provided by MESMER (see the mesRestraint docstring for more information)
		restraint	- The empty restraint object to be filled
		"""

		messages = []

		parser = argparse.ArgumentParser(prog=self.type[0])
		parser.add_argument('-file', 	action='store',								help='An external whitespace-delimited file containing LIST parameters.')
		parser.add_argument('-col', 	action='store',	type=int,	required=True,	help='The column of data to use as the restraint')
		parser.add_argument('-sse', 	action='store_true',						help='Calculate fitness as a simple (normalized) sum square of error')
		parser.add_argument('-harm', 	action='store_true',						help='Calculate fitness from a flat-bottomed harmonic, using the interval present in -col N+1')
		parser.add_argument('-Q', 		action='store_true',						help='Calculate fitness as an Q factor (quality factor).')
		parser.add_argument('-plot', 	action='store_true',						help='Create a plot window at each generation showing fit to data')

		try:
			args = parser.parse_args(block['header'].split()[2:])
		except argparse.ArgumentError, exc:
			return (False,["Argument error: %s" % exc.message()])

		restraint.data['args'] = args

		if (not args.sse) and (not args.harm) and (not args.Q):
			return(False,['Must specify at least one fitness calculation type!'])

		if(args.file):
			try:
				f = open(args.file)
				table = f.readlines()
				f.close()
			except:
				return(False,["Error reading from file \"%s\": %s" % (file,sys.exc_info()[1])])
		else:
			table = block['content']

		data = []
		for line in table:
			line = line.strip()
			data.append( [field.strip() for field in line.split()] )

		restraint.data['x'] = []
		restraint.data['y'] = []
		restraint.data['d'] = []  # only used in -harm

		for e in data:
			if( len(e) >= args.col ):
				key = '.'.join( e[:args.col] )
				restraint.data['x'].append(key)
				restraint.data['y'].append( float(e[args.col]) )

				# save error/interval information
				if(args.harm) and (len(e) >= args.harm):
					restraint.data['d'].append( float(e[args.harm]) )
				elif(args.harm):
					return(False,["Error determining harmonic interval from \"%s\". Line in question looks like: \"%s\""%(file,e)])

		return (True,messages)

	def load_attribute( self, attribute, block, ensemble_data ):
		"""
		Initializes the provided attribute with information from a component file

		Returns a two-element list containing the exit status (True for success, or False on failure) and a string describing the error (if any).

		Arguments:
		ensemble_data	- The plugin's data storage variable for this ensemble
		block			- The block dict provided by MESMER
		attribute		- The empty attribute object to be filled
		"""

		messages = []

		parser = argparse.ArgumentParser(prog=self.name)
		parser.add_argument('-file',	action='store',	help='An external whitespace-delimited file containing LIST parameters.')

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
				return(False,["Error reading from file \"%s\": %s" % (file,sys.exc_info()[1])])
		else:
			table = block['content']

		data = []
		for line in table:
			line = line.strip()
			data.append( [field.strip() for field in line.split()] )

		col = attribute.restraint.data['args'].col

		temp = {}
		temp['y'] = [0.0]*len(attribute.restraint.data['x'])
		seen = attribute.restraint.data['x'][:]
		for e in data:
			key = '.'.join( e[:col] )
			if( key in attribute.restraint.data['x'] ):
				i = attribute.restraint.data['x'].index(key)
				temp['y'][ i ] = float(e[col])
				seen.remove(key)

		for n in seen:
			messages.append("Couldn't find key \"%s\"!" % n)
		if( len(seen)>0 ):
			return(False,messages)

		# save the data to the database
		attribute.data['key'] = self.put(data=temp)

		return (True,messages)

	def load_bootstrap( self, bootstrap, restraint, ensemble_data, target_data ):
		"""
		Generates a bootstrap restraint using the provided ensemble data

		Arguments:
		bootstrap		- mesRestraint, the restraint to fill with the bootstrap sample
		restraint		- mesRestraint, the restraint serving as the template for the sample
		ensemble_data	- The plugin's data storage variable for this ensemble
		target_data		- The plugin's data storage variable for the target
		"""

		bootstrap.data['x'] = restraint.data['x']
		bootstrap.data['y'] = tools.make_bootstrap_sample( restraint.data['y'], ensemble_data['y'] )
		bootstrap.data['d'] = restraint.data['d']

		return (True,[])

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		"""
		Calculates the fitness of a set of attributes against a given restraint

		Returns a fitness score, which is actually the reduced chi-squared goodness-of-fit value between the restraint SAXS profile and the weighted-sum component SAXS profiles (attributes)

		Arguments:
		ensemble_data	- The plugin's data storage variable for the ensemble
		restraint		- The restraint object to be fitted against
		attributes		- A list of attributes to be averaged together and compared to the restraint
		ratios			- The relative weighting (ratio) of each attribute
		"""

		assert(len(attributes) == len(ratios))

		n = len(restraint.data['x'])

		# average the attribute data
		ensemble_data['y'] = tools.make_weighted_avg( [self.get(a.data['key'])['y'] for a in attributes], ratios )

		if( restraint.data['args'].sse ):
			return get_sse( restraint.data['y'], ensemble_data['y'] )

		elif( restraint.data['args'].harm ):
			return sum([tools.get_flat_harmonic(restraint.data['y'][i],restraint.data['d'][i],ensemble_data['y'][i]) for i in range(n)])

		elif( restraint.data['args'].Q ):
			# Calculate quality (Q) factor
			# Described in Cornilescu et al. (1998) J. Am. Chem. Soc.

			# calculate the RMS of the experimental data, store if not already present
			if(not 'rms' in restraint.data):
				restraint.data['rms'] = tools.get_rms(restraint.data['y'])

			diffs = [ restraint.data['y'][i] - ensemble_data['y'][i] for i in range(n) ]
			return tools.get_rms(diffs) / restraint.data['rms']
