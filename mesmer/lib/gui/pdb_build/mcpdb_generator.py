import os
import time
import random

from multiprocessing	import Process
from copy import deepcopy

from mcpdb_objects import *

class PDBGenerator(Process):
	def __init__(self,in_queue,out_queue,pdb,groups,outputdir,prefix='',format='%05i.pdb',fix_first=False,use_rama=False,eval_kwargs={},seed=0):
		super(PDBGenerator, self).__init__()
		self.iQ = in_queue
		self.oQ = out_queue
		self.daemon = True
		
		self.outputdir	= outputdir
		self.prefix	= prefix
		self.format	= format

		self.use_rama	= use_rama
		self.fix_first	= fix_first
		self.seed = int(time.time() + seed)
		
		self.model	= TransformationModel(pdb,groups,model=0)
		self.evaluator	= ModelEvaluator(self.model,**eval_kwargs)
		self.linkers = self.model.get_linker_phipsi()
								
	def run(self):
		if self.use_rama:
			import mcpdb_ramachandran as rama
			rama.set_seed( self.seed )
		else:
			import random
			random.seed( self.seed )

		for index in iter(self.iQ.get, None):
			while True:

				tmp = deepcopy(self.linkers)
				for l in tmp:
					for i in xrange(len(l)):
						if self.use_rama:
							l[i] = rama.get_random_Phi_Psi(radians=True)
						else:
							l[i] = 2*3.14159*random.random(),2*3.14159*random.random()
				
				self.model.set_linker_phipsi( tmp )

				if self.evaluator.check():
					if not self.fix_first:
						self.model.tumble()

					self.model.savePDB( os.path.join(self.outputdir,self.prefix+(self.format%(index))) )
					break

			self.oQ.put( index )

		return