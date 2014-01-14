from math import exp,sqrt,pi
from scipy import integrate,recfromtxt
from Bio.PDB.PDBParser import PDBParser

def getPDBElements( file, QD_name, QA_name ):
	"""
	Reads the specified file and returns an array containing all matching ATOM records.
	"""
	parser=PDBParser(PERMISSIVE=True,QUIET=True)
	structure=parser.get_structure("temp", file )
	
	donors = []
	acceptors = []
	
	for model in structure:
		for chain in model:
			for residue in chain:
				for atom in residue:
					if( atom.name == QD_name ):
						donors.append( atom )
					if( atom.name == QA_name ):
						acceptors.append( atom )

	return (donors,acceptors)
pass

def getPDBDistances( Donors, Acceptors, SkipChain, SkipModel ):
	"""
	Provided a set of PDB coordinates for donor and acceptors, builds an array of distances between them
	Note: excludes 0 distances (where donor == acceptor coordinates)
	"""
	distances = []
	for D in Donors:
		for A in Acceptors:
			if( SkipChain and (D.parent.parent == A.parent.parent) ):
				break
			if( SkipModel and (D.parent.parent.parent == A.parent.parent.parent) ):
				break
			
			# calculate the distance between acceptor and donor
			distance = A-D
			if( distance > 0.0 ):
				distances.append(distance)
	return distances
pass

def Pr( r, dR, distances ):
	"""
	Evaluates the probability function at a specific radius given a system of donor and acceptor fluorophores distributed with dR uncertainty
	"""
	if(len(distances)==0):
		return 0.0
		
	sum = 0.0
	for distance in distances:
		sum += 1/(dR*sqrt(2*pi))*exp(-0.5*((distance-r)/dR)**2)
	return sum / len(distances)
pass
	
def makePDBPr( distances, dR ):
	"""
	Given a set of Donor and Acceptor FRET coordinates, returns the Pr function evaluated at 1 Angstrom intervals to R + 10*dR
	"""
	ret = [0.0]*int(max(distances)+5*dR)
	for r in range(len(ret)):
		ret[r] = Pr(r,dR,distances)
	return ret
pass

def I_D( t, T_Di, T_Ai ):
	"""
	Returns the donor fluorescence intensity at a given time, assuming no FRET process
	"""
	sum = 0.0
	for i in range(len(T_Di)):
		sum += T_Ai[i]*exp( -1*(t/T_Di[i]) )
	return sum
pass

def I_Dr(t, r, T_Di, T_Ai, R0):
	"""
	Returns the donor fluorescence intensity at a given time and distance (r) from an acceptor
	"""
	sum = 0.0
	for i in range(len(T_Di)):
		sum += T_Ai[i]*exp( -1*(t/T_Di[i]) -1*(t/T_Di[i])*(R0/r)**6 )
	return sum
pass
	
def I_DA( t, T_Di, T_Ai, R0, distances, dR, fA ):
	"""
	Returns the donor fluorescence intensity at a given time t in a system of donors + acceptors at various distances
	"""
	if(len(distances) > 0):
		func = lambda r,t,T_Di,T_Ai,R0,distances: Pr(r,dR,distances) * I_Dr(t,r,T_Di,T_Ai,R0)
		A = (1-fA) * I_D(t,T_Di,T_Ai)
		B = fA * integrate.quad( func, 0, R0*5.0, args=(t,T_Di,T_Ai,R0,distances) )[0]
		return A+B
	else:
		return I_D(t,T_Di,T_Ai)
pass

# I_DA global for caching
_I_DA_values = None

def N_t( t, T_Di, T_Ai, R0, distances, dR, fA, IRF ):
	"""
	Returns the convolution of the donor intensity and the instrument response function (IRF)
	"""
	global _I_DA_values
	
	# precalc I_DA values
	if(_I_DA_values == None):
		_I_DA_values = [0]*len(IRF[0])
		for i in range(len(IRF[0])):
			_I_DA_values[i] = I_DA(IRF[0][i],T_Di,T_Ai,R0,distances,dR,fA)
	pass
		
	N_t = 0.0
	max = IRF[0].index(t)
	for i in range( max ):
		N_t += IRF[1][i] * _I_DA_values[ max -i ]
	pass
		
	return N_t
pass