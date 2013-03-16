import random
import scipy.interpolate
import scipy.optimize

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
	Get the optimal scaling factor between two single-dimension vectors

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
	
	# should raise error, but eh
	if( b == 0 ):
		return 0.0
		
	return a / b

def get_offset( y, y_fit, fraction=1.0):
	"""
	Get the necessary offset transformation between two single-dimension vectors
	
	Returns the offset value
	
	Arguments:
	y			- list of floats, the experimental dataset
	y_fit		- list of floats, the fitted values
	fraction	- float, the fraction of datapoints to use to determine the offset, defaults to 1 (all points).
	"""
	
	n = len(y)
	if (fraction >= 0):
		list = range( 0, int(n * fraction) )
	else:
		list = range( int(n * fraction * -1.0), n )

	y_avg, y_fit_avg = 0.0, 0.0
	for i in list:
		y_avg += y[ i ]
		y_fit_avg += y_fit[ i ]
		
	return (y_avg - y_fit_avg) / len(list)

def get_curve_transforms( y, dy, y_fit ):
	"""
	Get the scaling and offset transformations between two single-dimension vectors
	
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
	
def make_weighted_vector( vectors, weights ):
	"""
	Generate a vector sum
	
	Returns: the weighted z-dimensional vector sum
	
	Arguments:
	vectors		- list of n z-dimensional vectors
	weights		- list of n floats to be used as respective weights
	"""
	
	n = len(vectors[0])
	
	sum = [0.0] * n
	for (i,v) in enumerate(vectors):	
		for j in range(n):
			sum[j] += v[j] * weights[i]
	
	return sum
	
def make_bootstrap_sample( x, y, x_fit, y_fit ):
	"""
	Return a bootstrap estimate dataset for an experimental curve and associated best estimate
	
	Returns the bootstrap sample list of datapoints
	
	Arguments:
	y		- list of floats, the experimetnal dataset
	y_fit	- list of floats, the best estimate
	"""

	n = len(y)
	residual = [0.0]*n
	bootstrap = interpolate_curve( x, x_fit, y_fit )
	
	for i in range(n):
		residual[i] = y[i] - bootstrap[i]
	
	for i in range(n):
		bootstrap[i] += random.choice(residual)
	
	return bootstrap
	
	
	
	
	