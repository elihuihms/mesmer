import scipy
import random

try:
	import scipy.weave as weave
except ImportError:
	_USE_WEAVE = False
else:
	_USE_WEAVE = True

_COMPILE_ARGS = ["-Wno-unused-variable"]

if(_USE_WEAVE):
	def get_sse( y, yfit ):
		y,yfit = array(y),array(yfit)
		code=\
		"""
		double sum=0;

		for (int i=0; i<Ny[0]; i++)
			sum += pow( (double) Y1(i) - (double) YFIT1(i), 2);
		return_val = sum;
		"""

		return weave.inline( code, ['y','yfit'], verbose=0, extra_COMPILE_ARGS=_COMPILE_ARGS )

	def get_chisq_reduced( y, dy, yfit ):
		y,dy,yfit = scipy.array(y),scipy.array(dy),scipy.array(yfit)
		code=\
		"""
		double sum=0;

		for (int i=0; i<Ny[0]; i++)
		{
			if( (double) DY1(i) == 0 )
				continue;

			sum += pow(( (double) Y1(i) - (double) YFIT1(i)) / (double) DY1(i), 2);
		}

		return_val = sum / Ny[0];
		"""

		return weave.inline( code, ['y','dy','yfit'], verbose=0, extra_COMPILE_ARGS=_COMPILE_ARGS )

	def get_scale( y, dy, yfit ):
		y,dy,yfit = scipy.array(y),scipy.array(dy),scipy.array(yfit)
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

		return weave.inline( code, ['y','dy','yfit'], verbose=0, extra_COMPILE_ARGS=_COMPILE_ARGS )

	def get_offset( y, yfit, index=0):
		y,yfit = scipy.array(y),scipy.array(yfit)
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

		return weave.inline( code, ['y','yfit','index'], verbose=0, extra_COMPILE_ARGS=_COMPILE_ARGS )

	def get_rms( a ):
		a = scipy.array(a)
		code=\
		"""
		double sum=0;

		for(int i=0; i<Na[0]; i++)
			sum += pow(A1(i),2);

		return_val = sqrt( sum / Na[0] );
		"""

		return weave.inline( code, ['a'], verbose=0, extra_COMPILE_ARGS=_COMPILE_ARGS )
else:
	def get_sse( y, y_fit ):
		"""
		Get the sum squared of error between y and y_fit
		"""

		# create local numpy copies
		y,y_fit = scipy.array(y),scipy.array(y_fit)

		diffs = y - y_fit
		return sum(scipy.square(diffs))

	def get_chisq_reduced( y, dy, y_fit ):
		"""
		Get the reduced chi-squared value between y and y_fit within the error band dy

		Arguments:
		y		- list of floats, the experimental dataset
		dy		- list of floats, the experimental uncertainty (sigma) for each datapoint
		y_fit	- list of floats, the fitted values
		"""

		# create local numpy copies
		y,dy,y_fit = scipy.array(y),scipy.array(dy),scipy.array(y_fit)

		n = len(y)
		diffs = y - y_fit
		diffs /= dy
		return sum(scipy.square(diffs)) / n

	def get_scale( y, dy, y_fit ):
		"""
		Get the optimal scaling factor to superimpose two lists

		Arguments:
		y		- list of floats, the experimental dataset
		dy		- list of floats, the experimental uncertainty (sigma) for each datapoint
		y_fit	- list of floats, the fitted values
		"""

		# create local numpy copies
		y,dy,y_fit = scipy.array(y),scipy.array(dy),scipy.array(y_fit)

		dy2 = scipy.square(dy)
		a = sum( y     * y_fit / dy2 )
		b = sum( y_fit * y_fit / dy2 )

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

		# create local numpy copies
		y,y_fit = scipy.array(y),scipy.array(y_fit)

		if( index == 0 ):
			a = sum( y )
			b = sum( y_fit )
			return ( a - b ) / len(y)

		n = len(y)
		a, b = 0.0, 0.0
		for i in range(index,n):
			a += y[ i ]
			b += y_fit[ i ]
		return ( a - b ) / (n-index)

	def get_rms( a ):
		"""
		Calculate the RMS of a list
		"""

		total = 0.0
		for f in a:
			total += f**2
		return scipy.sqrt( total / len(a) )

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

	# create local numpy copies
	y,dy,y_fit = scipy.array(y),scipy.array(dy),scipy.array(y_fit)

	# translate both y and y_fit means to zero
	a = scipy.mean( y )
	b = scipy.mean( y_fit )
	y -= a
	y_fit -= b

	scale = get_scale( y, dy, y_fit )

	return( scale, a - (b * scale) )

def interpolate_curve( x, int_x, int_y ):
	"""
	Interpolate one curve to another by spline fitting

	Returns a list of the scipy.interpolated y values

	Arguments:
	x		- list of x values over which to scipy.interpolate the curve
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

	# create local numpy copies
	y,y_fit = scipy.array(y),scipy.array(y_fit)

	residuals = y - y_fit
	return scipy.array([f + random.choice(residuals) for f in y_fit])

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

	# create local numpy copies
	y = scipy.array(y)

	estimates = interpolate_curve( x, x_fit, y_fit )
	residuals = y-estimates

	return scipy.array([f + random.choice(residuals) for f in estimates])

def get_volatility_ratio( y, y_fit ):
	"""
	Returns the volatility of ratio metric defined by Hura et al. in Nature Methods (2013)
	Note: assumes y and y_fit have been pre-binned!

	Arguments:
	y		- list of floats
	y_fit	- list of floats
	"""

	n = len(y)

	ratios = [0.0]*n
	for i in range(n): # get ratios
		ratios[i] = y[i] / y_fit[i]

	t = fsum(ratios)
	for i in range(n): # normalize ratios
		ratios[i] /= t

	r = 0.0 # sum absolute value of ratio to ratio variance
	for i in range(n -1):
		r += fabs( (ratios[i] - ratios[i+1]) / ((ratios[i] + ratios[i+1]) / 2.0) )
	return r
