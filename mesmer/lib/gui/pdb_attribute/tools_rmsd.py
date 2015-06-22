import tkMessageBox
import Bio.PDB

from math import sqrt

def rmsd(c1, c2):
	total, N = 0.0, len(c1)
	assert N == len(c2)
	for i in xrange(N):
		total += (c1[i][0]-c2[i][0])**2 + (c1[i][1]-c2[i][1])**2 + (c1[i][2]-c2[i][2])**2
	return sqrt( total / N )
  
def calculate(pdb,ref_atoms,ref_selector,sup_atoms,sup_selector):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',pdb)[0]
	except Exception as e:
		return True,(pdb,"Could not parse PDB file: %s"%(e))

	# superimpose models first
	if sup_atoms != None:
		if sup_selector == None:
			try:
				match_atoms = [res['CA'] for res in model.get_residues()]
			except KeyError:
				return True,(pdb,"Error extracting C-alpha atoms from model residues. Perhaps there are solvent or hetams present?")
		else:
			try:
				match_atoms = [model[sup_selector[0]][i]['CA'] for i in range(sup_selector[1],sup_selector[2])]
			except IndexError:
				return True,(pdb,"Could not find residue %i of chain %s in PDB"%(i,chain),)
		try:		
			superimposer = Bio.PDB.Superimposer()
			superimposer.set_atoms(sup_atoms,match_atoms)
			superimposer.apply( model.get_atoms() ) # move ALL of the atoms in the test model
		except Exception as e:
			return True,(pdb,"Failed to superimpose PDB %s"%(e))
	
	if ref_selector == None:
		try:
			match_coords = [res['CA'].get_coord() for res in model.get_residues()]
		except KeyError:
			return True,(pdb,"Error extracting C-alpha atoms from model residues. Perhaps there are solvent or hetams present?")
	else:
		try:
			match_coords = [model[ref_selector[0]][i]['CA'].get_coord() for i in range(ref_selector[1],ref_selector[2])]
		except IndexError:
			return True,(pdb,"Could not find residue %i of chain %s"%(i,chain))
	
	try:
		value = rmsd([a.get_coord() for a in ref_atoms],match_coords)
	except AssertionError:
		return True,(pdb,"Could not calculate RMSD, some of the residues present in the reference PDB are missing in PDB")

	return False,(pdb,value)

def setup( w ):
	try:
		parser	= Bio.PDB.PDBParser(QUIET=True)
		model	= parser.get_structure('',w.calc_RMSD_PDBPath.get())[0]
	except Exception as e:
		tkMessageBox.showerror("Error","Could not parse reference PDB.\n\nReason:\n%s"%(e),parent=w)
		return None
		
	if w.calc_RMSD_SuperimposeSel.get() == 0: # superimpose all residues
		try:
			sup_atoms = [res['CA'] for res in model.get_residues()]
		except KeyError:
			tkMessageBox.showerror("Error","Error extracting C-alpha atoms from model residues. Perhaps there are solvent or hetams present?",parent=w)
			return None
		sup_selector = None
	elif w.calc_RMSD_SuperimposeSel.get() == 1: # superimpose a portion
		sup_selector = w.calc_RMSD_SuperimposeChain.get(),w.calc_RMSD_SuperimposeResStart.get(),w.calc_RMSD_SuperimposeResEnd.get()
		try:
			sup_atoms = [model[sup_selector[0]][i]['CA'] for i in range(sup_selector[1],sup_selector[2])]
		except IndexError:
			tkMessageBox.showerror("Error","Could not find residue %i of chain %s in the reference PDB."%(i,chain),parent=w)
			return None		
	else: # don't superimpose before calculating RMSD
		sup_atoms = None
		sup_selector = None

	if w.calc_RMSD_CalcSel.get() == 0: # calculate RMSD using all residues
		try:
			ref_atoms = [res['CA'] for res in model.get_residues()]
		except KeyError:
			tkMessageBox.showerror("Error","Error extracting C-alpha atoms from model residues. Perhaps there are solvent or hetams present?",parent=w)
			return None

		ref_selector = None
	else: # only calculate RMSD for some
		ref_selector = w.calc_RMSD_CalcChain.get(),w.calc_RMSD_CalcResStart.get(),w.calc_RMSD_CalcResEnd.get()
		try:
			ref_atoms = [model[ref_selector[0]][i]['CA'] for i in range(ref_selector[1],ref_selector[2])]
		except IndexError:
			tkMessageBox.showerror("Error","Could not find residue %i of chain %s in the reference PDB."%(i,chain),parent=w)
			return None

	return ref_atoms,ref_selector,sup_atoms,sup_selector
