import os
import time
import random

from copy import deepcopy

from .. plugin_objects import guiCalcPlugin
from mcpdb_objects import *
import mcpdb_ramachandran as rama

class PDBGenerator(guiCalcPlugin):
	def setup(self,pdb,groups,outputdir,prefix='',format='%05i.pdb',fix_first=False,use_rama=False,eval_kwargs={}):
		super(PDBGenerator, self).__init__()
		self.daemon = True
		
		self.outputdir	= outputdir
		self.prefix	= prefix
		self.format	= format
		self.use_rama	= use_rama
		self.fix_first	= fix_first
		
		self.model	= TransformationModel(pdb,groups,model=0)
		self.evaluator	= ModelEvaluator(self.model,**eval_kwargs)
		self.linkers = self.model.get_linker_phipsi()

		if self.use_rama:
			rama.seed( int(time.time()) )
		else:
			random.seed( int(time.time()) )
		
	def calculate(self, index):
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

		return index