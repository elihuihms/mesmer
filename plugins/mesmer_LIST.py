"""
Creates a MESMER restraint from a general list of data (NOEs, Pseudocontact shifts, etc.)
"""

import argparse
import sys

from scipy import sqrt,mean,average,array,interpolate
from scipy.stats import linregress

from lib.plugin_objects import mesPluginError,mesPluginDB
import lib.plugin_tools as tools

class plugin( mesPluginDB ):

	def __init__(self, args):

		# call parent constructor first
		mesPluginDB.__init__(self, args)

		self.name = 'default_LIST'
		self.version = '2013.09.24'
		self.type = (
			'LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9',
			'TABL','TABL0','TABL1','TABL2','TABL3','TABL4','TABL5','TABL6','TABL7','TABL8','TABL9')

		self.target_parser = argparse.ArgumentParser(prog=self.name)
		self.target_parser.add_argument('-file', 	action='store',								help='An external whitespace-delimited file containing LIST parameters.')
		self.target_parser.add_argument('-rCol', 	action='store',	type=int,	required=True,	help='The column of data to use as the restraint')
		self.target_parser.add_argument('-dCol',	action='store', type=int,					help='The column of data to use as a restraint interval when fitting Harmonic restraints')
		self.target_parser.add_argument('-plot', 	action='store_true',						help='Create a plot window at each generation showing fit to data')
		self.target_parser.add_argument('-fitness',	default='',	choices=['','SSE','Harmonic','Quality','Rsquare'],
																				help='Method used to calculate goodness-of-fit. Leave blank to use chi squared with explict dY data specified by -dcol')

		self.component_parser = argparse.ArgumentParser(prog=self.name)
		self.component_parser.add_argument('-file',	action='store',	help='An external whitespace-delimited file containing LIST parameters.')

		self._plot_handles = {}

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
			raise mesPluginError('Could not open file \"%s\" for writing' % file_path)

		f.write("# (identifiers)\texp\tfit\n")
		for i in range(len(restraint.data['x'])):
			tmp = restraint.data['x'][i].replace('.',"\t")
			f.write("%s\t%.3E\t%.3E\n" % (tmp,restraint.data['y'][i],ensemble_data[0]['y'][i]) )
		f.close()

		if(restraint.data['args'].plot):
			self.showplot( restraint.type, restraint.data['y'], ensemble_data[0]['y'] )

		return []

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

		try:
			args = self.target_parser.parse_args(block['header'].split()[2:])
		except argparse.ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		restraint.data['args'] = args

		# restraint checking
		if( args.fitness=='' and not args.dCol ):
			raise mesPluginError('Must specify a column containing uncertainty values via -dCol when fitness is calculated via chisquare')
		if( args.fitness=='Harmonic' and not args.dCol ):
			raise mesPluginError('Must specify a column containing a fitting interval via -dCol when fitting Harmonic restraints')

		if(args.file):
			try:
				f = open(args.file)
				table = f.readlines()
				f.close()
			except:
				raise mesPluginError("Error opening file \"%s\" for reading: %s" % (file,sys.exc_info()[1]))
		else:
			table = block['content']

		data = []
		for line in table:
			line = line.strip()
			if( line != ''):
				data.append( [field.strip() for field in line.split()] )

		restraint.data['x'] = []
		restraint.data['y'] = []
		restraint.data['d'] = []

		keys = []
		for e in data:
			try:
				key = '.'.join( e[:args.rCol] )
				restraint.data['x'].append(key)
				restraint.data['y'].append( float(e[args.rCol]) )
			except ValueError:
				raise mesPluginError("Error reading restraint value from provided target data. Line in question: \"%s\"" % (e))
			except IndexError:
				raise mesPluginError("Error reading restraint value from shortened line in target data. Line in question: \"%s\"" % (e))

			# save error/interval information
			if(args.fitness=='Harmonic' or args.fitness=='Harmonic'):
				try:
					restraint.data['d'].append( float(e[args.dCol]) )
				except ValueError:
					raise mesPluginError("Error determining harmonic interval value from provided target data. Line in question: \"%s\"" % (e))
				except IndexError:
					raise mesPluginError("Error obtaining harmonic interval value from shortened line in target data. Line in question: \"%s\"" % (e))

			if( key in keys):
				raise mesPluginError("Found a duplicate key (\"%s\") while reading target data." % (key))
			keys.append(key)

		return messages

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

		try:
			args = self.component_parser.parse_args(block['header'].split()[1:])
		except argparse.ArgumentError, exc:
			raise mesPluginError("Argument error: %s" % exc.message())

		if(args.file):
			try:
				f = open(args.file)
				table = f.readlines()
				f.close()
			except:
				raise mesPluginError("Error opening file \"%s\" for reading: %s" % (file,sys.exc_info()[1]))
		else:
			table = block['content']

		data = []
		for line in table:
			line = line.strip()
			if(line != ''):
				data.append( [field.strip() for field in line.split()] )

		temp = {}
		temp['y'] = [0.0]*len(attribute.restraint.data['x'])
		seen = attribute.restraint.data['x'][:]
		for e in data:
			key = '.'.join( e[:attribute.restraint.data['args'].rCol] )
			if( key in attribute.restraint.data['x'] ):
				try:
					i = attribute.restraint.data['x'].index(key)
					temp['y'][ i ] = float(e[attribute.restraint.data['args'].rCol])
					seen.remove(key)
				except ValueError:
					raise mesPluginError("Error determining harmonic interval value from provided target data. Line in question: \"%s\"" % (e))
				except IndexError:
					raise mesPluginError("Error obtaining harmonic interval value from shortened line in target data. Line in question: \"%s\"" % (e))

		for n in seen:
			messages.append("Couldn't find key \"%s\"!" % n)
		if( len(seen)>0 ):
			raise mesPluginError( "\n".join(messages) )

		# save the data to the database
		attribute.data['key'] = self.put(data=temp)

		return messages

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

		return []

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

		# average the attribute data - this is slow due to the lookup penalty each time. Optimize?
		ensemble_data['y'] = average( [self.get(a.data['key'])['y'] for a in attributes], 0, ratios )

		if( restraint.data['args'].fitness=='SSE' ):
			return get_sse( restraint.data['y'], ensemble_data['y'] )

		elif( restraint.data['args'].fitness=='Harmonic' ):
			n = len(restraint.data['x'])
			return sum([tools.get_flat_harmonic(restraint.data['y'][i],restraint.data['d'][i],ensemble_data['y'][i]) for i in range(n)])

		elif( restraint.data['args'].fitness=='Quality' ):
			# Calculate quality (Q) factor
			# Described in Cornilescu et al. (1998) J. Am. Chem. Soc.

			# calculate the RMS of the experimental data, cache if not already present
			if(not 'rms' in restraint.data):
				restraint.data['rms'] = tools.get_rms(array(restraint.data['y']))

			return tools.get_rms(restraint.data['y'] - ensemble_data['y']) / restraint.data['rms']
		elif( restraint.data['args'].fitness=='Rsquared' ):
			(slope,intercept,r,p,stderr) = linregress( restraint.data['y'], ensemble_data['y'] )
			return 1.0/(r**2)
		else:
			return tools.get_chisq_reduced( restraint.data['y'], restraint.data['d'], ensemble_data['y'] )
