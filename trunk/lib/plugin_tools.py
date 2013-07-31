import math
import random
import scipy.interpolate
import scipy.optimize

_use_weave = False

if(_use_weave):
	from scipy.weave import inline
	try:
		a = [ random.random() for i in range(10) ]
		n = len(a)
		code=\
		"""
		double sum=0;

		for(int i=0; i<n; i++)
			sum += (double) a[i];
		return_val = sum;
		"""
		inline( code, ['n','a'] )
	except:
		#print "WARNING : plugin_tools.py - weave compiler failure"
		_use_weave = False

if(_use_weave):
	print "INFO: Using compiled C versions of plugin_tools"

	def get_sse( y, y_fit ):

		#assert( isinstance(y,list) )
		#assert( isinstance(y_fit,list) )

		n = len(y)
		code=\
		"""
		double sum=0;

		for (int i=0; i<n; i++)
			sum += pow( (double) y[i] - (double) y_fit[i], 2);
		return_val = sum;
		"""

		return inline( code, ['n','y','y_fit'], verbose=0 )

	def get_chisq_reduced( y, dy, y_fit ):

		#assert( isinstance(y,list) )
		#assert( isinstance(dy,list) )
		#assert( isinstance(y_fit,list) )

		n = len(y)
		code=\
		"""
		double sum=0;

		for (int i=0; i<n; i++)
		{
			if( dy[i] == 0 )
				continue;

			sum += pow(( (double) y[i] - (double) y_fit[i]) / (double) dy[i], 2);
		}

		return_val = sum/(n -1);
		"""

		return inline( code, ['n','y','dy','y_fit'], verbose=0 )

	def get_scale( y, dy, y_fit ):

		#assert( isinstance(y,list) )
		#assert( isinstance(dy,list) )
		#assert( isinstance(y_fit,list) )

		n = len(y)
		code=\
		"""
		double a=0;
		double b=0;
		double c;

		for(int i=0; i<n; i++)
		{
			if( dy[i] == 0 )
				continue;

			c = pow((double) dy[i], 2);
			a += ((double) y_fit[i] * (double) y[i]) / c;
			b += ((double) y_fit[i] * (double) y_fit[i]) / c;
		}

		if( b == 0 )
			return_val = 0;
		else
			return_val = a / b;

		"""

		return inline( code, ['n','y','dy','y_fit'], verbose=0 )

	def get_offset( y, y_fit, index=0):

		#assert( isinstance(y,list) )
		#assert( isinstance(y_fit,list) )

		n = len(y)
		code=\
		"""
		double y_avg=0;
		double y_fit_avg=0;

		for(int i=index; i<n; i++)
		{
			y_avg += (double) y[i];
			y_fit_avg += (double) y_fit[i];
		}

		return_val = (y_avg - y_fit_avg) / (n - index);
		"""

		return inline( code, ['n','y','y_fit','index'], verbose=0 )
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

	spline = scipy.interpolate.splrep( int_x, int_y );
	return scipy.interpolate.splev( x, spline )

def make_weighted_avg( vectors, weights ):
	"""
	Generate a weighted sum of two lists

	Returns: the weighted z-dimensional list sum

	Arguments:
	vectors		- list of n z-dimensional lists
	weights		- list of n floats to be used as respective weights
	"""

	n = len(vectors[0])

	sum = [0.0] * n
	for (i,v) in enumerate(vectors):
		for j in range(n):
			sum[j] += v[j] * weights[i]

	return sum

def make_bootstrap_sample( x, x_fit ):
	"""
	Return a bootstrap estimate dataset for an experimental curve and associated best estimate

	Returns the bootstrap sample list of datapoints

	Arguments:
	x		- list of floats, the experimental dataset
	x_fit	- list of floats, the best estimate
	"""

	n = len(x)
	assert(n == len(x_fit))

	residuals = [0.0]*n
	bootstrap = [0.0]*n
	for i in range(n):
		residuals[i] = x[i] - x_fit[i]
		bootstrap[i] = x_fit[i]

	for i in range(n):
		bootstrap[i] += random.choice(residuals)

	return bootstrap

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

	n = len(y)
	residual = [0.0]*n
	bootstrap = interpolate_curve( x, x_fit, y_fit )

	for i in range(n):
		residual[i] = y[i] - bootstrap[i]

	for i in range(n):
		bootstrap[i] += random.choice(residual)

	return bootstrap

def get_rms( a ):
	"""
	Calculate the RMS of a list
	"""

	sum = 0.0
	for f in a:
		sum += f**2
	return math.sqrt( sum / len(a) )
