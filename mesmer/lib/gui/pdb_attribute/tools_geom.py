import Bio.PDB

from numpy import std

def calculate_rg(pdb,CA_only):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',pdb)[0]
	except Exception as e:
		return True,(pdb,"Could not parse PDB file: %s"%(e))

	try:
		if CA_only:
			coords = [r['CA'].get_coord() for r in model.get_residues()]
			masses = [1.0]*len(coords)
		else:
			coords = [a.get_coord()*a.mass for a in model.get_atoms() if a.mass != float('NaN')]
			masses = [a.mass for a in model.get_atoms() if a.mass != float('NaN')]
	except Exception as e:
		return True,(pdb,"Error reading atoms from PDB: %s"%(e))
		
	N = len(coords)
	CoM = sum(coords) / N
	return False,(pdb,std([c-CoM for c in coords])/(sum(masses)/N)) #@TODO@ - check this

def calculate_distance(pdb,A,B):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',pdb)[0]
	except Exception as e:
		return True,(pdb,"Could not parse PDB file: %s"%(e))

	try:
		return False,(pdb,model[A[0]][A[1]][A[2]]-model[B[0]][B[1]][B[2]])
	except Exception as e:
		return True,(pdb,"Error reading specified atoms from PDB: %s"%(e))

def calculate_angle(pdb,A,B,C):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',pdb)[0]
	except Exception as e:
		return True,(pdb,"Could not parse PDB file: %s"%(e))

	try:
		vA = model[A[0]][A[1]][A[2]].get_vector()
		vB = model[B[0]][B[1]][B[2]].get_vector()
		vC = model[C[0]][C[1]][C[2]].get_vector()
	except Exception as e:
		return True,(pdb,"Error reading specified atoms from PDB: %s"%(e))
	return False,(pdb,Bio.PDB.calc_angle(vA,vB,vC))

def calculate_dihedral(pdb,A,B,C,D):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',pdb)[0]
	except Exception as e:
		return True,(pdb,"Could not parse PDB file: %s"%(e))

	try:
		vA = model[A[0]][A[1]][A[2]].get_vector()
		vB = model[B[0]][B[1]][B[2]].get_vector()
		vC = model[C[0]][C[1]][C[2]].get_vector()
		vD = model[D[0]][D[1]][D[2]].get_vector()
	except Exception as e:
		return True,(pdb,"Error reading specified atoms from PDB: %s"%(e))

	return False,(pdb,Bio.PDB.calc_dihedral(vA,vB,vC,vD))

def setup_rg(w):
	return [w.calc_Rg_AtomSel.get()==0]

def setup_distance(w):
	cA = w.calc_Distance_SelA_Chain.get()
	rA = w.calc_Distance_SelA_Res.get()
	aA = w.calc_Distance_SelA_Atom.get()
	cB = w.calc_Distance_SelB_Chain.get()
	rB = w.calc_Distance_SelB_Res.get()
	aB = w.calc_Distance_SelB_Atom.get()
	return (cA,rA,aA),(cB,rB,aB)

def setup_angle(w):
	cA = w.calc_Angle_SelA_Chain.get()
	rA = w.calc_Angle_SelA_Res.get()
	aA = w.calc_Angle_SelA_Atom.get()
	cB = w.calc_Angle_SelB_Chain.get()
	rB = w.calc_Angle_SelB_Res.get()
	aB = w.calc_Angle_SelB_Atom.get()
	cC = w.calc_Angle_SelC_Chain.get()
	rC = w.calc_Angle_SelC_Res.get()
	aC = w.calc_Angle_SelC_Atom.get()
	return (cA,rA,aA),(cB,rB,aB),(cC,rC,aC)
	
def setup_dihedral(w):
	cA = w.calc_Dihedral_SelA_Chain.get()
	rA = w.calc_Dihedral_SelA_Res.get()
	aA = w.calc_Dihedral_SelA_Atom.get()
	cB = w.calc_Dihedral_SelB_Chain.get()
	rB = w.calc_Dihedral_SelB_Res.get()
	aB = w.calc_Dihedral_SelB_Atom.get()
	cC = w.calc_Dihedral_SelC_Chain.get()
	rC = w.calc_Dihedral_SelC_Res.get()
	aC = w.calc_Dihedral_SelC_Atom.get()
	cD = w.calc_Dihedral_SelD_Chain.get()
	rD = w.calc_Dihedral_SelD_Res.get()
	aD = w.calc_Dihedral_SelD_Atom.get()
	return (cA,rA,aA),(cB,rB,aB),(cC,rC,aC),(cD,rD,aD)
