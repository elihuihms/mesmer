import math

def get_atom_coords(file,chainID=None,resNum=None,atomName='CA'):

	f = open(file, 'r')

	ret = []

	line = f.readline()
	while( line ):

		if (line[0:4] != 'ATOM') and (line[0:6] != 'HETATM'):
			line = f.readline()
			continue

		if (line[21]==chainID) or (chainID==None):
			if (int(line[22:26])==int(resNum)) or (resNum==None):
				if( line[12:16].strip() == atomName ):
					ret.append( (float(line[30:38]),float(line[38:46]),float(line[46:54])) )

		line = f.readline()
	f.close()

	return ret

def get_distance( file, chainA, resA, atomA, chainB, resB, atomB ):
	"""
	Return the distance (in angstroms) between two atoms defined by a chain, residue number, and atom name in a pdb
	Raises an Exception if anything other than a single set of coordinates is matched
	"""
	coordsA = get_atom_coords( file, chainA, resA, atomA )
	coordsB = get_atom_coords( file, chainB, resB, atomB )

	if(len(coordsA)==0):
		raise Exception("Did not find any coordinates in \"%s\" matching %s:%s:%s" % (chainA, resA, atomA))
	if(len(coordsB)==0):
		raise Exception("Did not find any coordinates in \"%s\" matching %s:%s:%s" % (chainB, resB, atomB))
	if(len(coordsA)>1):
		raise Exception("Found %i sets of coordinates in \"%s\" matching %s:%s:%s" % (len(coordsA), chainA, resA, atomA))
	if(len(coordsB)>1):
		raise Exception("Found %i sets of coordinates in \"%s\" matching %s:%s:%s" % (len(coordsB), chainB, resB, atomB))

	return math.sqrt( (coordsA[0][0]-coordsB[0][0])**2 + (coordsA[0][1]-coordsB[0][1])**2 + (coordsA[0][2]-coordsB[0][2])**2 )

def make_distribution( mu, sigma ):
	"""
	Return a gaussian distribution dict
	"""

	distances = []
	for r in range( int(max(0, mu-(sigma*4) )), int(mu+(sigma*4)) ):
		distances.append( (r, 1.0 / (sigma * math.sqrt(2*math.pi)) * math.exp( -0.5 * ((r - mu) / sigma)**2 )) )

	return distances
