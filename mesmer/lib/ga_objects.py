import sys
import os.path

from math					import fabs
from scipy					import optimize
from multiprocessing		import Process,Queue

from exceptions				import *

class Optimizer:
	def __init__(self,args,plugins,targets,components):
		self.workers = [None]*args.threads
		self.in_Queue,self.out_Queue = Queue(maxsize=args.threads),Queue()
						
		for i in xrange(args.threads):
			self.workers[i] = Worker(args, plugins, targets, components, self.in_Queue, self.out_Queue)
			self.workers[i].start()

		return
		
	def optimize(self,ensembles,print_status=True):
		n,i = len(ensembles),0
		divisor = int(max(n/100,1))
		ret = []
		
		# submit ensembles to the queue
		for i in xrange(n):
			self.in_Queue.put( ensembles[i] )
		
			if(i % divisor == 0 and print_status):
				sys.stdout.write("\tComponent ratio optimization progress: %i%%\r" % (1+100.*i/n) )
				sys.stdout.flush()
			
			# do we have any optimized ensembles to retrieve?
			try:
				ret.append( self.out_Queue.get(False) )
			except:
				pass
		
		# retrieve optimized ensembles
		while len(ret) < n:
			ret.append( self.out_Queue.get(True) )
						
		return ret
		
	def close(self):
		for w in self.workers:
			self.in_Queue.put(None)	
		
		for w in self.workers:
			w.join()
		return

class Worker(Process):
	def __init__(self,args,plugins,targets,components,in_queue,out_queue):
		super(Worker, self).__init__()
		self.args = args
		self.plugins = plugins
		self.targets = targets
		self.components = components
		self.iQ = in_queue
		self.oQ = out_queue
		self.daemon = True

	def run(self):
		
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
					(e.ratios[t.name],nfeval,status) = optimize.fmin_tnc( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=self.args.Rn, messages=0, accuracy=self.args.Rprecision )
					e.opt_status[t.name] = optimize.tnc.RCSTRINGS[status]
	
				elif( self.args.Ralgorithm == 4 ):
					(e.ratios[t.name],fopt,status) = optimize.fmin_l_bfgs_b( wrapper, e.ratios[t.name], fprime=None, approx_grad=True, bounds=ratio_bounds, maxfun=self.args.Rn, disp=False, epsilon=self.args.Rprecision)
					e.opt_status[t.name] = status['warnflag']
	
				elif( self.args.Ralgorithm == 5 ):
					(e.ratios[t.name],fopt,direc,iters,funcalls,e.opt_status[t.name]) = optimize.fmin_powell(wrapper, e.ratios[t.name], disp=0, full_output=True, maxfun=self.args.Rn, xtol=self.args.Rprecision)
	
				elif( self.args.Ralgorithm == 6 ):
					(e.ratios[t.name],fopt,iters,funcalls,e.opt_status[t.name]) = optimize.fmin( wrapper, e.ratios[t.name], xtol=self.args.Rprecision, maxfun=self.args.Rn, full_output=True, disp=False)
	
				# set optimization flag!
				if( (e.opt_status[t.name] != 0) or self.args.Rforce ):
					e.optimized[t.name] = False
				else:
					e.optimized[t.name] = True
	
				# normalize ensemble ratios for the target
				e.normalize(t.name)
	
			self.oQ.put( e )
		
		return
