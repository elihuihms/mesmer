from Bio.PDB import *
from numpy import array

class TransformationGroup():
	def __init__(self,residues,children=[]):
		self._rigid_residues	= residues
		self._linker_residues	= []
		self.linker_length		= len(self._linker_residues)
		self._morph_direction	= 0
		self._children			= children
					
	def add_residues(self,residues):
		self._rigid_residues.extend(residues)
	
	def get_residues(self):
		if self._morph_direction > 0:
			return self._linker_residues+self._rigid_residues
		else:
			return self._rigid_residues+self._linker_residues
			
	def get_children(self):
		return self._children
					
	def set_linker_residues(self,residues,direction):
		self._linker_residues	= residues
		self._morph_direction	= direction
		self.linker_length		= len(self._linker_residues)
		
	def get_termini(self):
		termini = {}
		for r in self.get_residues():
			foo1, model, chain, (foo2, resnum, foo3) = r.get_full_id()
			if chain not in termini:
				termini[chain] = [resnum,resnum]
			else:
				if resnum < termini[chain][0]:
					termini[chain][0] = resnum
				if resnum > termini[chain][1]:
					termini[chain][1] = resnum
		return termini
		
	def print_hierarchy(self,depth=0):
		for i,r in enumerate(self.get_residues()):
			foo1, model, chain, (foo2, resnum, foo3) = r.get_full_id()
		
			if r in self._linker_residues:
				info = "%s %i L"%(chain,resnum)
			else:
				info = "%s %i  "%(chain,resnum)
			print "%s%i	%s"%("\t"*depth,i+depth,info)

		for i,c in enumerate(self._children):
			print "%sCHILD %i"%("\t"*depth,i)
			c.print_hierarchy(depth+1)
			
	def get_linker_phipsi(self):
		ret = []
		for i in xrange(1,self.linker_length-1):
			N	= self._linker_residues[i]['N'].get_vector()
			CA	= self._linker_residues[i]['CA'].get_vector()
			C	= self._linker_residues[i]['C'].get_vector()
			NN	= self._linker_residues[i+1]['N'].get_vector()
			CP	= self._linker_residues[i-1]['C'].get_vector()

			ret.append( (calc_dihedral(CP,N,CA,C),calc_dihedral(N,CA,C,NN)) )
		return ret
					
	def apply_transformation(self, rotation_array ):
		assert( len(rotation_array) == self.linker_length -2 )

		if self._morph_direction > 0: # N to C direction
			for i in xrange(1,self.linker_length-1):
				self._rotate_phi( i, rotation_array[i-1][0] )
				self._rotate_psi( i, rotation_array[i-1][1] )
		else:
			for i in xrange(self.linker_length-2,0,-1):
				self._rotate_psi( i, rotation_array[i-1][1] )
				self._rotate_phi( i, rotation_array[i-1][0] )
		return
		
	def rotate(self, r, t=None):
		r = r.astype('f')

		atoms = self.get_atoms()
		n = len(atoms)

		if t == None:
			coords = [a.get_coords() for a in atoms]
			t = array(coords/n,'f')
		else:
			t = t.astype('f')

		for atom in self.get_atoms():
			atom.transform(r, t)

	def _rotate_phi(self, i, angle ):
		if angle == None:
			return
			
		N	= self._linker_residues[i]['N'].coord
		CA	= self._linker_residues[i]['CA'].coord
		m = rotaxis2m( angle, Vector(CA - N) )
		t = array((0,0,0),'f')

		for j in xrange(i,self.linker_length):
			for a in self._linker_residues[j]:
				if j==i and (a.name=='N' or a.name=='H' or a.name=='HN'):
					continue
				a.coord = a.coord - CA
				a.transform( m, t )
				a.coord = a.coord + CA
				
		for r in self._rigid_residues:
			for a in r:
				a.coord = a.coord - CA
				a.transform( m, t )
				a.coord = a.coord + CA
		return

	def _rotate_psi(self, i, angle ):
		if angle == None:
			return
			
		C = self._linker_residues[i]['C'].coord
		CA	= self._linker_residues[i]['CA'].coord
		m = rotaxis2m( angle, Vector(C - CA) )
		t = array((0,0,0),'f')

		for j in xrange(i,self.linker_length):
			for a in self._linker_residues[j]:
				if j==i and a.name!='O':
					continue
				a.coord = a.coord - C
				a.transform( m, t )
				a.coord = a.coord + C

		for r in self._rigid_residues:
			for a in r:
				a.coord = a.coord - C
				a.transform( m, t )
				a.coord = a.coord + C
		return
											
class TransformationModel():
	
	def __init__(self, pdb, group_specifiers=[], model=0):
		self.parser		= PDBParser()
		self.structure	= self.parser.get_structure('',pdb)
		self.model		= self.structure[model]
		
		self._assigned_residues = []
		if group_specifiers == []:
			return
		
		# create a list of residues that are to be held rigid
		self._rigid_groups,self._rigid_residues = [],[]
		for group_specifier in group_specifiers:
			residues = []
			for chain,start,end in group_specifier:
				residues.extend( self._get_residues(chain,start,end) )
			self._rigid_groups.append( TransformationGroup(residues[:]) )
			self._rigid_residues.extend( residues[:] )
										
		# recursively assign transformationGroups
		self._transformation_group = self._get_children( self._rigid_groups[0] )
	
	def print_hierarchy(self):
		self._transformation_group.print_hierarchy() 
		
	def _get_residues(self, chain, start, end):
		return [self.model[chain][resnum] for resnum in xrange(min(start,end+1),max(start,end+1)) ]

	def _get_residue(self, chain, resnum):
		try:
			return self.model[chain][resnum]
		except KeyError:
			return None
	
	def _get_children(self, group):

		group_residues = group.get_residues()
		self._assigned_residues.extend( group_residues )		
		group_children = []
				
		for chain,(start,end) in group.get_termini().iteritems():			
			A,B = self._chain_iterator( chain, end, +1)
			group_residues.extend(A)
			group_children.extend(B)
			
			A,B = self._chain_iterator( chain, start, -1)
			group_residues.extend(A)
			group_children.extend(B)
			
		ret = TransformationGroup(group_residues,group_children)
		return ret
		
	def _chain_iterator(self, chain, start, direction ):
		linker_residues = []		
		group_residues,group_children = [],[]
	
		resnum = start +direction
		residue = self._get_residue(chain,resnum)
		if residue != None and residue not in self._assigned_residues:
			exit = False
			while not exit and residue != None:														
				if residue in self._assigned_residues:
					raise Exception("CYCLIC")
									
				if residue in self._rigid_residues:
					for testgroup in self._rigid_groups:
						testresidues = testgroup.get_residues()
						if residue in testresidues:

							group_children.append( self._get_children(testgroup) )
							group_children[-1].set_linker_residues( linker_residues, direction )
							group_residues.extend( group_children[-1].get_residues() )
							linker_residues = []

							exit = True
							break							
				else:
					linker_residues.append( residue )
					self._assigned_residues.append( residue )
									
				resnum += direction
				residue = self._get_residue(chain,resnum)
		
		# catch any tails w/o rigid bodies attached
		if linker_residues != []:
			group_children.append( TransformationGroup([],[]) )
			group_children[-1].set_linker_residues( linker_residues, direction )
			group_residues.extend( group_children[-1].get_residues() )
			
		return group_residues,group_children
		
	def get_linker_phipsi(self):
		def _recursive( group, ret ):
			for i,g in enumerate(group.get_children()):
				ret.append( g.get_linker_phipsi() )
				_recursive( g, ret )
		
		ret = []
		_recursive( self._transformation_group, ret )
		return ret
		
	def set_linker_phipsi(self, rotation_array):
		def _recursive( group ):
			for i,g in enumerate(group.get_children()):
				g.apply_transformation( rotation_array[0] )
				rotation_array.pop(0)
				_recursive( g )
		
		_recursive( self._transformation_group )
		
	def savePDB(self,path):
		output = PDBIO()
		output.set_structure( self.structure )
		output.save(path)

class ModelEvaluator():

	def __init__(self, model, clash_radius=3.6, CA_only=True, clash_cutoff=0):
		self.model			= model.model
		self.clash_radius	= clash_radius
		self.clash_cutoff	= clash_cutoff

		self.atoms = []
		for a in self.model.get_atoms():
			if CA_only and a.name=='CA':
				self.atoms.append(a)
			elif not CA_only:
				self.atoms.append(a)

		self.natoms = len(self.atoms)
		return

	def check(self):
		clash_counter = 0
		for i in xrange(self.natoms):
			for j in xrange(i+1,self.natoms):
				if self.atoms[i]-self.atoms[j] < self.clash_radius:
					clash_counter += 1
				
				if clash_counter > self.clash_cutoff:
					return False

		return True

	def count_clashes(self):
		c = 0
		for i in xrange(self.natoms):
			for j in xrange(i+1,self.natoms):
				if self.atoms[i]-self.atoms[j] < self.clash_radius:
					c+=1
		return c



