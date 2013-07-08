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
import scipy
import scipy.interpolate as interpolate

from StringIO import StringIO

from lib.plugin_primitives import plugin_db
import lib.plugin_tools as tools


class plugin( plugin_db ):

	name = 'default_SAXS'
	version = '2013.06.04'
	type = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')

	_plot_handles = {}

	#
	# output functions
	#

	def show_best_plot(self,id,x,y,yfit,diff):

		try:
			import matplotlib.pyplot as plot
		except:
			print "Could not load matplotlib!"
			return

		plot.ion()

		if(not id in self._plot_handles.keys()):
			self._plot_handles[id] = {}
			self._plot_handles[id]['counter'] = 0
			self._plot_handles[id]['fig'] = plot.figure()

		plot.figure(self._plot_handles[id]['fig'].number)
		self._plot_handles[id]['fig'].clear()
		self._plot_handles[id]['main'] = self._plot_handles[id]['fig'].add_axes([0.1,0.1,0.8,0.8])
		plot.title("Best MESMER fit to \"%s\" data" % id)
		plot.yscale('log')
		plot.ylabel('I(q), intensity')
		plot.xlabel(r'$q, \AA^{-1}$')

		self._plot_handles[id]['exp'] = plot.plot(x, y, 'ro' )
		self._plot_handles[id]['fit'] = plot.plot(x, yfit )

		self._plot_handles[id]['inset'] = self._plot_handles[id]['fig'].add_axes([0.5,0.5,0.35,0.35])
		plot.title('Residuals')
		plot.yscale('linear')
		plot.ylabel(r'$I(q)_{exp} / I(q)_{fit}$')
		self._plot_handles[id]['diff'] = plot.plot(x, diff, 'ro' )
		plot.setp(self._plot_handles[id]['inset'], xlim=(0,0.2) )

		plot.draw()
		plot.ioff()

		return

	def ensemble_state( self, restraint, target_data , ensembles, file_path):
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
			return (False,['Could not open file \"%s\" for writing' % file_path])

		f.write("# Best scoring ensemble fit\n" )
		f.write("# scale: %.3e\n" % (ensembles[0]['scale']) )
		f.write("# offset: %.3e\n" % (ensembles[0]['offset']) )
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

		parser = argparse.ArgumentParser(prog=self.name)
		parser.add_argument('-file', 	metavar='FILE',			help='Path to external file containing SAXS data if not contained in the target file')
		parser.add_argument('-scale', 	action='store_true',	help='Scale the component profiles for a better match to the target profile')
		parser.add_argument('-bg', 	action='store_true',	help='Apply a small offset to improve fit at high q angles')
		parser.add_argument('-offset', 		action='store_true',	help='Perform background subtraction to better match the target profile.')
		parser.add_argument('-plot', 	action='store_true',	help='Create a plot window at each generation showing fit to data')

		try:
			args = parser.parse_args(block['header'].split()[2:])
		except argparse.ArgumentError, exc:
			return (False,["Argument error: %s" % exc.message()])

		target_data['args'] = args

		# attempt to load the SAXS profile
		if(args.file == None):
			try:
				values = scipy.genfromtxt( StringIO( ''.join(block['content'])), unpack=True )
			except ValueError, exc:
				return (False,["Could not parse SAXS data in target file - %s " % (exc)])
		else:
			try:
				values = scipy.genfromtxt(args.file, unpack=True)
			except ValueError, exc:
				return (False,["Could not read file \"%s\" - %s" % (args.file, exc)])

		if(len(values) != 3):
			return (False,["Target SAXS data must be of the format: x y dy"])

		restraint.data['x'] = values[0]
		restraint.data['y'] = values[1]
		restraint.data['d'] = values[2]

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
		parser.add_argument('-file', metavar='FILE', help='Path to external file containing SAXS data if not contained in the target file')

		try:
			args = parser.parse_args(block['header'].split()[1:])
		except argparse.ArgumentError, exc:
			return (False,["Argument error: %s" % exc.message()])

		if(args.file == None):
			try:
				values = scipy.genfromtxt( StringIO( ''.join(block['content'])), unpack=True )
			except ValueError, exc:
				return (False,["Could not parse SAXS data in component file - %s" % (exc)])
		else:
			try:
				values = scipy.genfromtxt(args.file, unpack=True)
			except ValueError, exc:
				return (False,["Could not read file \"%s\" - %s" % (args.file, exc)])

		if(len(values) != 2):
			return (False,["Component SAXS data must be of the format: x y"])

		# attempt to interpolate the XY values against the target restraint X values
		try:
			temp = interpolate.splrep( values[0], values[1] )
			interpolate.splev( attribute.restraint.data['x'],temp )
		except TypeError:
			return (False,["Could not interpolate the component's SAXS curve to the target's"])

		# save the spline to the database
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
		bootstrap.data['y'] = tools.make_interpolated_bootstrap_sample( restraint.data['x'], restraint.data['y'], ensemble_data['x'], ensemble_data['y'] )
		bootstrap.data['d'] = restraint.data['d']

		return (True,[])

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		"""
		Calculates the fitness of a set of attributes against a given restraint

		Returns a fitness score, which is actually the reduced chi-squared goodness-of-fit value between the restraint SAXS profile and the weighted-sum component SAXS profiles (attributes)

		Arguments:
		ensemble_data	- The plugin's data storage variable for the ensemble
		restraint		- The restraint object to be fitted against
		attrbutes		- A list of attributes to be averaged together and compared to the restraint
		ratios			- The relative weighting (ratio) of each attribute
		"""

		assert(len(attributes) == len(ratios))

		n = len(restraint.data['x'])

		# average the attribute profiles
		fit = tools.make_weighted_vector( [interpolate.splev(restraint.data['x'], self.get(a.data['key'])) for a in attributes], ratios )

		# determine the scaling and/or offset coefficients
		if(target_data['args'].scale and target_data['args'].offset):
			(ensemble_data['scale'],ensemble_data['offset']) = tools.get_curve_transforms( list(restraint.data['y']) , restraint.data['d'], fit[:] )
		elif(target_data['args'].scale):
			ensemble_data['scale'] = tools.get_scale( restraint.data['y'], restraint.data['d'], fit[:] )
			ensemble_data['offset'] = 0.0
		elif(target_data['args'].offset):
			ensemble_data['scale'] = 1.0
			ensemble_data['offset'] = tools.get_offset( restraint.data['y'], fit[:] )
		else:
			ensemble_data['scale'] = 1.0
			ensemble_data['offset'] = 0.0

		# apply the scaling and offset coefficients to the dataset
		for i in range(n):
			fit[i] = (fit[i] * ensemble_data['scale']) + ensemble_data['offset']

		# determine high-q offset
		if(target_data['args'].bg):
			ensemble_data['high_q_offset'] = tools.get_offset( restraint.data['y'], fit, -0.750 )

			for i in range(n):
				fit[i] += ensemble_data['high_q_offset']
		else:
			ensemble_data['high_q_offset'] = 0.0

		# Save all of these parameters to the ensemble_data object for future retrieval
		ensemble_data['x'] = restraint.data['x']
		ensemble_data['y'] = fit

		return tools.get_chisq_reduced( restraint.data['y'], restraint.data['d'], fit )

