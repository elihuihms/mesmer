from math import cos,pi,sqrt,exp
from Bio.PDB.PDBParser import PDBParser
from scipy import integrate

def getAtomCoords(file,chainID=None,resNum=None,atomName='CA'):

	f = open(file, 'r')

	ret = []

	line = f.readline()
	while( line ):

		if (line[0:4] != 'ATOM') and (line[0:6] != 'HETATM'):
			line = f.readline()
			continue

		if (line[21]==chainID) or (chainID==None):
			if (int(line[22:26])==resNum) or (resNum==None):
				if( line[12:16].strip() == atomName ):
					ret.append( (float(line[30:38]),float(line[38:46]),float(line[46:54])) )

		line = f.readline()
	f.close()

	return ret

def writeAtomLine( handle, a ):

	#                    s   n   R   N  R      X  Y  Z  O  B        S  E
	handle.write( "ATOM  %5d %4s %3s %1s%4s    %8s%8s%8s%6s%6s      %4s%2s  \n" % (
		a['serial'],
		a['name'].center(4),
		a['resname'],
		a['chain'],
		a['resnum'],
		str("%.3f" % a['coords'][0]).rjust(8),
		str("%.3f" % a['coords'][1]).rjust(8),
		str("%.3f" % a['coords'][2]).rjust(8),
		str("%.2f" % a['occupancy']).rjust(6),
		str("%.2f" % a['bfactor']).rjust(6),
		a['segment'],
		a['element'])
	)
	return

def getDistance(coord1,coord2):
	return sqrt( (coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2 + (coord1[2]-coord2[2])**2 )

def getAverage(coord1,coord2):
	return ( ((coord1[0]+coord2[0])/2),((coord1[1]+coord2[1])/2),((coord1[2]+coord2[2])/2) )

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

def addToDistribution( d, v, p ):
	# keys are the value's (v) multiple of precision (p)
	v = round(v/p)
	if v in d:
		d[ v ] += 1
	else:
		d[ v ] = 1

def reducedChisq( y, dy, y_fit ):

	n = len(y)
	sum = 0.0
	for i in range( n ):
		if(dy[i] == 0.0):
			continue
		sum += ( (y[i] - y_fit[i]) / dy[i] )**2

	return sum/(n -1)