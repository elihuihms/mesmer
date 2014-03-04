from math import cos,pi,exp
from scipy import integrate

def DipolarFreq( D_dip, r ):
	return 2*pi*D_dip/r**3

def DEER( D_dip, r, t, dW=None ):

	def f(x):
		tmp = cos( (3*x**2-1) * DipolarFreq(D_dip,r) * t )
		if(dW!=None):
			return exp( -1*DipolarFreq(D_dip,r)**2/dW**2) * tmp
		return tmp

	return integrate.quad( f, 0, 1.0 )[0]


def DEER_Vt( D_dip, distances, t, dW=None ):

	avg = 0.0
	for (r,w) in distances:
		if(r>0):
			avg += DEER( D_dip, r, t, dW )*w

	return avg