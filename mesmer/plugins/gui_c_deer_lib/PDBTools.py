import math
import scipy
import scipy.linalg

def get_atom_coords(handle,chainID=None,resNum=None,atomName='CA'):

	handle.seek(0) # rewind handle

	ret,line = [],handle.readline()
	while( line ):

		if (line[0:4] != 'ATOM') and (line[0:6] != 'HETATM'):
			line = handle.readline()
			continue

		if (line[21]==chainID) or (chainID==None):
			if (int(line[22:26])==int(resNum)) or (resNum==None):
				if( line[12:16].strip() == atomName ):
					ret.append( (float(line[30:38]),float(line[38:46]),float(line[46:54])) )

		line = handle.readline()

	return ret

def get_distance( handle, chainA, resA, atomA, chainB, resB, atomB ):
	"""
	Return the distance (in angstroms) between two atoms defined by a chain, residue number, and atom name in a pdb
	Raises an Exception if anything other than a single set of coordinates is matched
	"""

	coordsA = get_atom_coords( handle, chainA, resA, atomA )
	coordsB = get_atom_coords( handle, chainB, resB, atomB )

	if(len(coordsA)==0 or len(coordsA)>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coordsA), chainA, resA, atomA))
	if(len(coordsB)==0 or len(coordsB)>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coordsB), chainB, resB, atomB))

	return math.sqrt( (coordsA[0][0]-coordsB[0][0])**2 + (coordsA[0][1]-coordsB[0][1])**2 + (coordsA[0][2]-coordsB[0][2])**2 )

def get_alignment( handle, chainA, resA, atomA1, atomA2, chainB, resB, atomB1, atomB2 ):
	"""
	Returns the colinearity of two vectors obtained from four atom positions
	"""

	coords = []
	coords.append( scipy.array( get_atom_coords( handle, chainA, resA, atomA1 ), float) )
	coords.append( scipy.array( get_atom_coords( handle, chainA, resA, atomA2 ), float) )
	coords.append( scipy.array( get_atom_coords( handle, chainB, resB, atomB1 ), float) )
	coords.append( scipy.array( get_atom_coords( handle, chainB, resB, atomB2 ), float) )

	if(len(coords[0])==0 or len(coords[0])>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coords[0]), chainA, resA, atomA1))
	if(len(coords[1])==0 or len(coords[1])>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coords[1]), chainA, resA, atomA2))
	if(len(coords[2])==0 or len(coords[2])>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coords[2]), chainB, resB, atomB1))
	if(len(coords[3])==0 or len(coords[3])>1):
		raise Exception("Found %i sets of coordinates matching %s:%s:%s" % (len(coords[3]), chainB, resB, atomB2))

	# generate vectors
	a1 = (coords[1] - coords[0])[0]
	a2 = (coords[2] - coords[0])[0]
	b1 = (coords[3] - coords[2])[0]
	b2 = (coords[0] - coords[2])[0]

	# normalize vectors
	a1/= scipy.linalg.norm(a1)
	a2/= scipy.linalg.norm(a2)
	b1/= scipy.linalg.norm(b1)
	b2/= scipy.linalg.norm(b2)

	# return colinearity
	return scipy.dot( a1, a2 ) + scipy.dot( b1, b2 )

def make_distribution( mu, sigma ):
	"""
	Return a gaussian distribution dict
	"""

	distances = []
	for r in range( int(max(0, mu-(sigma*4) )), int(mu+(sigma*4)) ):
		distances.append( (r, 1.0 / (sigma * math.sqrt(2*math.pi)) * math.exp( -0.5 * ((r - mu) / sigma)**2 )) )

	return distances
