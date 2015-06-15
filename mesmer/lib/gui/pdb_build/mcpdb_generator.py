import os

from multiprocessing	import Process
from random import random
from copy import deepcopy

from mcpdb_objects import *

class PDBGenerator(Process):
	def __init__(self,in_queue,out_queue,pdb,groups,use_rama=False,fix_first=False,dir='',prefix='',format='%05i.pdb',eval_kwargs={}):
		super(PDBGenerator, self).__init__()
		self.iQ = in_queue
		self.oQ = out_queue
		self.daemon = True
		
		self.outputdir	= dir
		self.prefix	= prefix
		self.format	= format

		self.use_rama	= use_rama
		self.fix_first	= fix_first
		
		self.model	= TransformationModel(pdb,groups,model=0)
		self.evaluator	= ModelEvaluator(self.model,**eval_kwargs)
		self.linkers = self.model.get_linker_phipsi()
						
	def run(self):
		if self.use_rama:
			import mcpdb_ramachandran as ramachandran
	
		for index in iter(self.iQ.get, None):
			
			while True:
				tmp = deepcopy(self.linkers)
				for l in tmp:
					for i in xrange(len(l)):
					
						if self.use_rama:
							l[i] = ramachandran.get_random_Phi_Psi(radians=True)
						else:
							l[i] = 2*3.14159*random(),2*3.14159*random()
				
				self.model.set_linker_phipsi( tmp )

				if self.evaluator.check():
					filename = self.prefix+(self.format%(index))

					if not self.fix_first:
						self.model.tumble()

					self.model.savePDB( os.path.join(self.outputdir,filename) )
					break

			self.oQ.put( index )

		return