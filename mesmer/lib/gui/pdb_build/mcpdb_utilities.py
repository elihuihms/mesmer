import os
import glob

from Bio.PDB import *

def get_chain_info( path ):
	parser		= PDBParser()
	structure	= parser.get_structure('',path)
	model		= structure[0]
	
	chains = {}
	for chain in model:
		chains[ chain.id ] = [None,None]
		
		for r in chain:
			if chains[ chain.id ][0] == None:
				chains[ chain.id ][0] = r.id[1]
			chains[ chain.id ][1] = r.id[1]
	
	return chains

def check_groups( path, groups, model=0):
	parser		= PDBParser()
	structure	= parser.get_structure('',path)
	model		= structure[model]

	assigned_ranges = {}

	for group in groups:
		for chain,start,end in group:
			if chain not in assigned_ranges.keys():
				assigned_ranges[chain] = []
				
			if start in assigned_ranges[chain]:
				return 2,"Residue %i of chain %s assigned to two groups"%(start,chain)
			if end in assigned_ranges[chain]:
				return 2,"Residue %i of chain %s assigned to two groups"%(start,chain)

			assigned_ranges[chain].extend( range( min(start,end), max(start,end) ) )
				
			try:
				f = model[chain][start]
			except:
				return 1,"Residue %i in chain %s not found"%(start,chain)
			try:
				f = model[chain][end]
			except:
				return 1,"Residue %i in chain %s not found"%(end,chain)
				
	return 0,None
	
def check_PDB( path, model=0 ):
	# returns:
	# 0,None if ok
	# 1 if break
	
	parser		= PDBParser()
	structure	= parser.get_structure('',path)
	model		= structure[model]
		
	for chain in model:
		prev_resnum = None
		for r in chain:
			f1, m, c, (f2, resnum, f3) = r.get_full_id()
			if prev_resnum != None:
				if resnum != prev_resnum +1:
					return 1,"Discontinuity in chain %s (jumped from %i to %i)"%(c,prev_resnum,resnum)
			
			prev_resnum = resnum
	
	return 0,None
	
	
	
