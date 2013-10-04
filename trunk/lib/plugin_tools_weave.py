from scipy import array
from scipy.weave import inline

_compile_args = ["-Wno-unused-variable"]

def get_sse( y, yfit ):
	y,yfit = array(y),array(yfit)
	code=\
	"""
	double sum=0;

	for (int i=0; i<Ny[0]; i++)
		sum += pow( (double) Y1(i) - (double) YFIT1(i), 2);
	return_val = sum;
	"""

	return inline( code, ['y','yfit'], verbose=0, extra_compile_args=_compile_args )

def get_chisq_reduced( y, dy, yfit ):
	y,dy,yfit = array(y),array(dy),array(yfit)
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

	return inline( code, ['y','dy','yfit'], verbose=0, extra_compile_args=_compile_args )

def get_scale( y, dy, yfit ):
	y,dy,yfit = array(y),array(dy),array(yfit)
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

	return inline( code, ['y','dy','yfit'], verbose=0, extra_compile_args=_compile_args )

def get_offset( y, yfit, index=0):
	y,yfit = array(y),array(yfit)
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

	return inline( code, ['y','yfit','index'], verbose=0, extra_compile_args=_compile_args )

def get_rms( a ):
	a = array(a)
	code=\
	"""
	double sum=0;

	for(int i=0; i<Na[0]; i++)
		sum += pow(A1(i),2);

	return_val = sqrt( sum / Na[0] );
	"""

	return inline( code, ['a'], verbose=0, extra_compile_args=_compile_args )

# run tests to precompile
_test_y = array([0.8481512759,0.6583598928,0.6846607752,0.5538229567,0.6578159478,0.6068740106,0.4426829643,0.3179492581,0.383121644,0.3765805775,0.3708506186,0.3058596196,0.3024194233,0.2234957702,0.1393319385,0.1900480675,0.1120111097,0.3743889742,0.2114251276,0.174838398,0.032248709,0.1400864056,0.1523370291,0.0580405721])
_test_dy = array([0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1])
_test_yfit = array([0.904837418,0.8187307531,0.7408182207,0.670320046,0.6065306597,0.5488116361,0.4965853038,0.4493289641,0.4065696597,0.3678794412,0.3328710837,0.3011942119,0.272531793,0.2465969639,0.2231301601,0.201896518,0.1826835241,0.1652988882,0.1495686192,0.1353352832,0.1224564283,0.1108031584,0.1002588437,0.0907179533])

_test_sum = \
	get_sse(_test_y,_test_yfit) \
	+get_chisq_reduced(_test_y,_test_dy,_test_yfit) \
	+get_scale(_test_y,_test_dy,_test_yfit)	\
	+get_offset(_test_y,_test_yfit) \
	+get_rms(_test_y)

if( int(_test_sum) != 2 ):
	raise

del _test_y
del _test_dy
del _test_yfit

