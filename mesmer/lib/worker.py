import scipy
import multiprocessing

from mesmer.lib.optimizers import *

class Worker(multiprocessing.Process):
	def __init__(self,optimizer):
		super(Worker, self).__init__()
		
		self.args = optimizer.args
		self.plugins = optimizer.plugins
		self.targets = optimizer.targets
		self.components = optimizer.components
		self.iQ = optimizer.in_queue
		self.oQ = optimizer.out_queue
		self.daemon = True

	def run(self):
		"""Consume ensembles from the input queue, and calculate their cumulative fitness score
		
		Arguments: None
		
		Returns: None
		"""
		
		# retrieve ensembles from the queue
		for e in iter(self.iQ.get, None):
		
			# set up a bounding array for bounded optimizers
			ratio_bounds = [(0.0,1.0)] * self.args.size
		
			# optimize for each target individually
			for (i,t) in enumerate(self.targets):
	
				# delta function for fitness algorithm to pass to minimization function
				def wrapper( ratios ):
					return sum(e.get_fitness( self.components, self.plugins, t, ratios ).itervalues())
	
				if(e.optimized[t.name]):
					continue
				elif( self.args.Ralgorithm == 0 ):
					e.get_fitness( components, plugins, t, [1.0/self.args.size] * self.args.size )
					e.opt_status[t.name] = 'N/A'
	
				elif( self.args.Ralgorithm == 1 ):
					e.ratios[t.name] = blind_random_min( wrapper, e.ratios[t.name], self.args.Rprecision, self.args.Rn )
					e.opt_status[t.name] = 'N/A'
	
				elif( self.args.Ralgorithm == 2 ):
					e.ratios[t.name] = localized_random_min( wrapper, e.ratios[t.name], self.args.Rprecision, self.args.Rn )
					e.opt_status[t.name] = 'N/A'
	
				elif( self.args.Ralgorithm == 3 ):
					(e.ratios[t.name],nfeval,status) = scipy.optimize.fmin_tnc( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=self.args.Rn, messages=0, accuracy=self.args.Rprecision )
					e.opt_status[t.name] = scipy.optimize.tnc.RCSTRINGS[status]
	
				elif( self.args.Ralgorithm == 4 ):
					(e.ratios[t.name],fopt,status) = scipy.optimize.fmin_l_bfgs_b( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=self.args.Rn, disp=False, epsilon=self.args.Rprecision)
					e.opt_status[t.name] = status['warnflag']
	
				elif( self.args.Ralgorithm == 5 ):
					(e.ratios[t.name],fopt,direc,iters,funcalls,e.opt_status[t.name]) = scipy.optimize.fmin_powell(wrapper, e.ratios[t.name], disp=0, full_output=True, maxfun=self.args.Rn, xtol=self.args.Rprecision)
	
				elif( self.args.Ralgorithm == 6 ):
					(e.ratios[t.name],fopt,iters,funcalls,e.opt_status[t.name]) = scipy.optimize.fmin( wrapper, e.ratios[t.name], xtol=self.args.Rprecision, maxfun=self.args.Rn, full_output=True, disp=False)
	
				# set optimization flag!
				if( (e.opt_status[t.name] != 0) or self.args.Rforce ):
					e.optimized[t.name] = False
				else:
					e.optimized[t.name] = True
	
				# normalize ensemble ratios for the target
				e.normalize(t.name)
	
			self.oQ.put( e )
		
		return