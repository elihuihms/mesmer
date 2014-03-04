"""
	Creates a MESMER restraint from a 2D dataset
"""

import argparse
import math
import scipy
import scipy.interpolate as interpolate
import scipy.optimize as optimize

from StringIO import StringIO

from lib.plugin_objects import mesPluginError,mesPluginDB
import lib.plugin_tools as tools

class plugin( mesPluginDB ):

	def __init__(self, args):

		# call parent constructor first
		mesPluginDB.__init__(self, args)

		self.name = 'default_CURV'
		self.version = '2013.11.22'
		self.type = (
			'CURV','CURV0','CURV1','CURV2','CURV3','CURV4','CURV5','CURV6','CURV7','CURV8','CURV9',
			'SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9',
			'DEER','DEER0','DEER1','DEER2','DEER3','DEER4','DEER5','DEER6','DEER7','DEER8','DEER9'
			)

		self.target_parser = argparse.ArgumentParser(prog=self.name)
		self.target_parser.add_argument('-file',		metavar='FILE', 		help='Read an external file containing the experimental data')
		self.target_parser.add_argument('-scale',		action='store_true',	help='Allow scaling of the calculated curve to improve fitting')
		self.target_parser.add_argument('-offset',		action='store_true',	help='Allow the application of an offset to improve fitting')
		self.target_parser.add_argument('-saxs_offset', type=float,				help='Improve fits to SAXS curves at higher specified scattering angles by applying an additional offset.')
		self.target_parser.add_argument('-plot',		action='store_true',	help='Create a plot window at each generation showing fit to data (requires matplotlib)')
		self.target_parser.add_argument('-fitness',		default='',	choices=['','SSE','Pearson','Poisson','Vr'],
																				help='Method used to calculate goodness-of-fit. Leave blank to use chi squared with explict dY data')

		self.component_parser = argparse.ArgumentParser(prog=self.name)
		self.component_parser.add_argument('-file',		metavar='FILE',			help='Read an external file containing the predicted data')

		self._plot_handles = {}

	def showplot(self,id,x,y,yfit,saxs=False):

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

		if(saxs):
			plot.yscale('log')
			plot.ylabel('I(q), intensity')
			plot.xlabel(r'$q, \AA^{-1}$')
		else:
			plot.ylabel('Y')
			plot.xlabel('X')

		self._plot_handles[id]['exp'] = plot.plot(x, y, 'ro' )
		self._plot_handles[id]['fit'] = plot.plot(x, yfit )
		self._plot_handles[id]['inset'] = self._plot_handles[id]['fig'].add_axes([0.5,0.5,0.35,0.35])

		diff = [0.0]*len(y)
		if(saxs):
			plot.yscale('linear')
			plot.ylabel(r'$I(q)_{exp} / I(q)_{fit}$')
			for i in range(len(y)):
				diff[i] = y[i] / yfit[i]
		else:
			plot.ylabel(r'$Y_{exp} - Y_{fit}$')
			for i in range(len(y)):
				diff[i] = y[i] - yfit[i]

		plot.title('Residuals')
		self._plot_handles[id]['diff'] = plot.plot(x, diff, 'ro' )
		plot.setp(self._plot_handles[id]['inset'], xlim=(0,0.2) )

		plot.draw()
		plot.ioff()

		return

	def ensemble_state( self, restraint, target_data, ensembles, file_path):
		"""
		Prints the status of the plugin for the current generation and target

		Returns a list of Error_state,output

		Arguments:
		target_data		- list of data the plugin has saved for the target
		ensembles		- list of data the plugin has saved for every ensemble in the run, ordered by overall fitness
		filePath		- an optional file path the plugin can save data to
		"""

		try:
			f = open( file_path, 'w' )
		except IOError:
			raise mesPluginError('Could not open file \"%s\" for writing' % file_path)

		f.write("# Best scoring ensemble fit\n" )
		if(ensembles[0]['scale'] != 1):
			f.write("# scale: %.3E\n" % (ensembles[0]['scale']) )
		if(ensembles[0]['offset'] != 0):
			f.write("# offset: %.3E\n" % (ensembles[0]['offset']) )
		if('saxs_offset' in ensembles[0]):
			f.write("# saxs offset: %.3E\n" % (ensembles[0]['saxs_offset']) )
		if('lambda' in ensembles[0]):
			f.write("# modulation depth: %.3E\n" % (ensembles[0]['lambda']) )

		f.write("#x\ty_exp\ty_fit\n" )

		# print the fit for the best-scoring ensemble
		y_fit = tools.interpolate_curve( restraint.data['x'], ensembles[0]['x'], ensembles[0]['y'] )

		for (i,x) in enumerate(restraint.data['x']):
			f.write( "%.3E\t%.3E\t%.3E\n" % (x,restraint.data['y'][i],y_fit[i]) )

		f.close()

		# generate a plot figure if necessary
		if(target_data['args'].plot):
			self.showplot( restraint.type, restraint.data['x'], restraint.data['y'], y_fit, (target_data['type'] == 'SAXS') )

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

		if(args.file == None):
			try:
				values = scipy.genfromtxt( StringIO( ''.join(block['content'])), unpack=True )
			except Exception as e:
				raise mesPluginError("Could not parse 2D data in target file - %s " % e)
		else:
			try:
				values = scipy.genfromtxt(args.file, unpack=True)
			except Exception as e:
				raise mesPluginError("Could not read file \"%s\" - %s" % (args.file, e))

		if( len(values) < 2 ):
			raise mesPluginError("Target data must contain at least two columns: x y")

		restraint.data['x'] = scipy.array(values[0])
		restraint.data['y'] = scipy.array(values[1])

		# autodetect restraint types
		if( restraint.type[0:4] == 'SAXS' ):
			target_data['type'] = 'SAXS'
		elif( restraint.type[0:4] == 'DEER' ):
			target_data['type'] = 'DEER'
		else:
			target_data['type'] = ''

		# argument consistency checks
		if( target_data['type'] == 'DEER' and (args.scale or args.offset) ):
			raise mesPluginError("Scaling or offset options not available when fitting DEER data")

		# set the per-point weighting to be used during fitting
		if( args.fitness == 'SSE' ): # X^2 = (Y - Y_fit)^2
			restraint.data['d'] = [1.0] * len(restraint.data['x'])

		elif( args.fitness == 'Pearson' ): # X^2 = ((Y - Y_fit) / Y)^2
			restraint.data['d'] = restraint.data['y']

		elif( args.fitness == 'Poisson' ): # X^2 = ((Y - Y_fit) / sqrt(Y))^2
			restraint.data['d'] = [ math.sqrt(y) for y in restraint.data['y'] ]

		elif(len(values) != 3):
			raise mesPluginError("Target data must be of the format: x y dy")

		else:
			# X^2 = ((Y - Y_fit) / dY)^2
			restraint.data['d'] = scipy.array(values[2])

		if( args.fitness == 'Vr' ): # volatility ratio - Hura et al. Nmeth. 2013
			# resample (bin) x values
			interval = (restraint.data['x'][-1] - restraint.data['x'][0]) / 30.0
			resample = scipy.arange( restraint.data['x'][0], restraint.data['x'][-1], interval )
			try:
				temp = interpolate.splrep( restraint.data['x'], restraint.data['y'] )
				restraint.data['y'] = interpolate.splev( resample, temp )
				restraint.data['x'] = resample
			except TypeError:
				raise mesPluginError("Could not interpolate target's curve data. Perhaps the x values are not ordered?")

		target_data['args'] = args

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

		if(args.file == None):
			try:
				values = scipy.genfromtxt( StringIO( ''.join(block['content'])), unpack=True )
			except Exception as e:
				raise mesPluginError("Could not parse 2D data in component file - %s" % e)
		else:
			try:
				values = scipy.genfromtxt(args.file, unpack=True)
			except Exception as e:
				raise mesPluginError("Could not read file \"%s\" - %s" % (args.file, e))

		if(len(values) != 2):
			raise mesPluginError("Component data must be at least of the format: x y")

		# attempt to interpolate the XY values against the target restraint X values
		try:
			temp = interpolate.splrep( values[0], values[1] )
			interpolate.splev( attribute.restraint.data['x'], temp )
		except TypeError:
			raise mesPluginError("Could not interpolate the component's curve data to the target's. Perhaps the x values are not ordered?")

		# save the spline to the database
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
		bootstrap.data['y'] = tools.make_interpolated_bootstrap_sample( restraint.data['x'], restraint.data['y'], ensemble_data['x'], ensemble_data['y'] )
		bootstrap.data['d'] = restraint.data['d']

		return []

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

		# average the attribute data - this is slow due to the lookup penalty each time. Optimize?
		ensemble_data['y'] = scipy.average([interpolate.splev(restraint.data['x'], self.get(a.data['key'])) for a in attributes],0,ratios)
		ensemble_data['x'] = restraint.data['x']

		# determine the scaling and/or offset coefficients
		if(target_data['args'].scale and target_data['args'].offset):
			(ensemble_data['scale'],ensemble_data['offset']) = tools.get_curve_transforms( restraint.data['y'] , restraint.data['d'], ensemble_data['y'] )
		elif(target_data['args'].scale):
			ensemble_data['scale'] = tools.get_scale( restraint.data['y'], restraint.data['d'], ensemble_data['y'] )
			ensemble_data['offset'] = 0.0
		elif(target_data['args'].offset):
			ensemble_data['scale'] = 1.0
			ensemble_data['offset'] = tools.get_offset( restraint.data['y'], ensemble_data['y'] )
		else:
			ensemble_data['scale'] = 1.0
			ensemble_data['offset'] = 0.0

		n = len(restraint.data['x'])

		# optimize modulation depth to fit DEER data
		if(target_data['type'] == 'DEER'):

			tmp = [0.0]*n
			def opt( l ):
				for i in range(n):
					tmp[i] = 1.0 -l +(l*ensemble_data['y'][i])
				return tools.get_chisq_reduced( restraint.data['y'], restraint.data['d'], scipy.array(tmp) )
			ensemble_data['lambda'] = optimize.brent( opt )

			ensemble_data['y'] = scipy.array([ 1.0 -ensemble_data['lambda'] + (ensemble_data['lambda']*f) for f in ensemble_data['y'] ])
		else:
			# apply the scaling and offset coefficients to the dataset
			ensemble_data['y'] *= ensemble_data['scale']
			ensemble_data['y'] += ensemble_data['offset']

		# apply additional small SAXS offset if necessary
		if(target_data['args'].saxs_offset):
			# determine starting q value index if not already calculated
			if( not 'saxs_offset_n' in target_data):
				for i in range(n):
					if( restraint.data['x'][i] > target_data['args'].saxs_offset ):
						target_data['saxs_offset_n'] = i
						break

			ensemble_data['saxs_offset'] = tools.get_offset( restraint.data['y'], ensemble_data['y'], target_data['saxs_offset_n'] )
			ensemble_data['y'] += ensemble_data['saxs_offset']

		if( target_data['args'].fitness == 'Vr' ):
			return tools.get_volatility_ratio( restraint.data['y'], ensemble_data['y'] )

		return tools.get_chisq_reduced( restraint.data['y'], restraint.data['d'], ensemble_data['y'] )
