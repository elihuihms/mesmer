import math
import random
import numpy
import scipy.interpolate
import scipy.optimize

_use_weave = True

if(_use_weave):
	from scipy.weave import inline
	try:
		test = numpy.array( [ random.random() for i in range(10) ] )
		code=\
		"""
		double sum=0;

		for(int i=0; i<Ntest[0]; i++)
			sum += (double) TEST1(i);
		return_val = sum;
		"""
		inline( code, ['test'] )
	except:
		print "WARNING : plugin_tools.py - weave compile failure"
		_use_weave = False

if(_use_weave):
	print "INFO: Using weave versions of plugin_tools"

	def get_sse( y, yfit ):
		code=\
		"""
		double sum=0;

		for (int i=0; i<Ny[0]; i++)
			sum += pow( (double) Y1(i) - (double) YFIT1(i), 2);
		return_val = sum;
		"""

		return inline( code, ['y','yfit'], verbose=0 )

	def get_chisq_reduced( y, dy, yfit ):
		code=\
		"""
		double sum=0;

		for (int i=0; i<Ny[0]; i++)
		{
			if( (double) DY1(i) == 0 )
				continue;

			sum += pow(( (double) Y1(i) - (double) YFIT1(i)) / (double) DY1(i), 2);
		}

		return_val = sum/(Ny[0] -1);
		"""

		return inline( code, ['y','dy','yfit'], verbose=0 )

	def get_scale( y, dy, yfit ):
		code=\
		"""
		double a=0;
		double b=0;
		double c;

		for(int i=0; i<Ny[0]; i++)
		{
			if( (double) DY1(i) == 0 )
				continue;

			c = pow((double) DY1(i), 2);
			a += ((double) YFIT1(i) * (double) Y1(i)) / c;
			b += ((double) YFIT1(i) * (double) YFIT1(i)) / c;
		}

		if( b == 0 )
			return_val = 0;
		else
			return_val = a / b;

		"""

		return inline( code, ['y','dy','yfit'], verbose=0 )

	def get_offset( y, yfit, index=0):
		code=\
		"""
		double y_avg=0;
		double y_fit_avg=0;

		for(int i=index; i<Ny[0]; i++)
		{
			y_avg += (double) Y1(i);
			y_fit_avg += (double) YFIT1(i);
		}

		return_val = (y_avg - y_fit_avg) / (Ny[0] - index);
		"""

		return inline( code, ['y','yfit','index'], verbose=0 )

	def get_rms( a ):
		code=\
		"""
		double sum=0;

		for(int i=0; i<Na[0]; i++)
			sum += pow(A1(i),2);

		return_val = sqrt( sum / Na[0] );
		"""

		return inline( code, ['a'], verbose=0 )

else:
	def get_sse( y, y_fit ):
		"""
		Get the sum squared of error between y and y_fit
		"""
		n = len(y)
		sum = 0.0
		for i in range( n ):
			sum += ( y[i] - y_fit[i] )**2

		return sum

	def get_chisq_reduced( y, dy, y_fit ):
		"""
		Get the reduced chi-squared value between y and y_fit within the error band dy

		Arguments:
		y		- list of floats, the experimental dataset
		dy		- list of floats, the experimental uncertainty (sigma) for each datapoint
		y_fit	- list of floats, the fitted values
		"""

		n = len(y)
		sum = 0.0
		for i in range( n ):
			if(dy[i] == 0.0):
				continue
			sum += ( (y[i] - y_fit[i]) / dy[i] )**2

		return sum/(n -1)

	def get_scale( y, dy, y_fit):
		"""
		Get the optimal scaling factor to superimpose two lists

		Arguments:
		y		- list of floats, the experimental dataset
		dy		- list of floats, the experimental uncertainty (sigma) for each datapoint
		y_fit	- list of floats, the fitted values
		"""

		(a,b) = (0.0,0.0)
		for i in range( len(y) ):
			if(dy[i] == 0.0):
				continue
			a += ( y_fit[i] * y[i] )/( dy[i]**2 )
			b += ( y_fit[i] * y_fit[i] )/( dy[i]**2 )

		if( b == 0 ):
			return 0.0

		return a / b

	def get_offset( y, y_fit, index=0):
		"""
		Get the necessary offset transformation to superimpose two lists

		Returns the offset value

		Arguments:
		y			- list of floats, the experimental dataset
		y_fit		- list of floats, the fitted values
		index		- starting index to use, defaults to 0 (all points)
		"""

		n = len(y)

		y_avg, y_fit_avg = 0.0, 0.0
		for i in range(index,n):
			y_avg += y[ i ]
			y_fit_avg += y_fit[ i ]

		return (y_avg - y_fit_avg) / (n-index)

	def get_rms( a ):
		"""
		Calculate the RMS of a list
		"""

		sum = 0.0
		for f in a:
			sum += f**2
		return math.sqrt( sum / len(a) )

def get_flat_harmonic( y, dy, y_fit, power=2 ):
	"""
	Returns a "flat-bottomed" harmonic potential (Nilges et al. 1988)
	"""
	high = y+dy
	low = y-dy

	if(y_fit < low):
		return (low - y_fit)**power / y
	elif(y_fit > high):
		return (y_fit -high)**power / y
	else:
		return 0.0

def get_curve_transforms( y, dy, y_fit ):
	"""
	Get the scaling and offset transformations to superimpose two lists

	Returns (scale,offset)

	Arguments:
	y			- list of n floats, the experimental dataset
	dy			- list of n floats, the experimental uncertainty (sigma) for each datapoint
	y_fit		- list of n floats, the fitted values
	"""

	# translate both y and y_fit means to zero
	n = len(y)
	y_avg = sum(y) / n
	y_fit_avg = sum(y_fit) / n

	for i in range(n):
		y[i] -= y_avg
		y_fit[i] -= y_fit_avg

	scale = get_scale( y, dy, y_fit )

	return( scale, y_avg - (y_fit_avg * scale) )

def interpolate_curve( x, int_x, int_y ):
	"""
	Interpolate one curve to another by spline fitting

	Returns a list of the interpolated y values

	Arguments:
	x		- list of x values over which to interpolate the curve
	int_x	- list of original x values
	int_y	- list of original y values
	"""

	return scipy.interpolate.splev( x, scipy.interpolate.splrep( int_x, int_y ) )

def make_bootstrap_sample( y, y_fit ):
	"""
	Return a bootstrap estimate dataset for an experimental curve and associated best estimate

	Returns the bootstrap sample list of datapoints

	Arguments:
	y		- list of floats, the experimental dataset
	y_fit	- list of floats, the best estimate
	"""

	n = len(y)
	assert(n == len(y_fit))

	residuals = [ y[i] - y_fit[i] for i in range(n) ]

	return [f + random.choice(residuals) for f in y_fit]

def make_interpolated_bootstrap_sample( x, y, x_fit, y_fit ):
	"""
	Return a bootstrap estimate dataset for an experimental X/Y curve and associated best X/Y estimate

	Returns the bootstrap sample list of datapoints

	Arguments:
	x		- list of floats, the experimental independent var
	y		- list of floats, the experimental dependent var
	x_fit	- list of floats, the fit dataset independent var
	y_fit	- list of floats, the fit dataset dependent var
	"""

	estimates = interpolate_curve( x, x_fit, y_fit )
	residuals = [ y[i] - estimates[i] for i in range(len(y)) ]

	return [f + random.choice(residuals) for f in estimates]

