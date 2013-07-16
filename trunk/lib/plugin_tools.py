import math
import random
import scipy.interpolate
import scipy.optimize
from scipy.weave import inline

def get_sse( y, y_fit ):
	"""
	Get the sum squared of error between y and y_fit
	"""

	code=\
	"""
		int i;
		float sum;
		for (i=0; i<n; i++)
			sum += pow(y[i] - y_fit[i],2);

		return sum;
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

	code=\
	"""
		int i;
		int n;
		float sum = 0.0;

		n = y.length();
		for (i=0; i<n; i++)
		{
			if( dy[i] == 0 )
				continue;

			sum += pow((y[i] - y_fit[i]) / dy[i],2);
		}

		return_val = sum/(n -1);
	"""

	n = len(y)
	sum = 0.0
	for i in range( n ):
		if(dy[i] == 0.0):
			continue
		sum += ( (y[i] - y_fit[i]) / dy[i] )**2

	return sum/(n -1)

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

	assert( b != 0 )
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
