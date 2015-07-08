import sys
import multiprocessing
import copy

try:
	import cPickle as pickle
except:
	import pickle
		
class FunctionWorker(multiprocessing.Process):
	def __init__(self,in_queue,out_queue):
		super(FunctionWorker, self).__init__()
		self.iQ,self.oQ = in_queue,out_queue
		self.daemon = True
		
	def setup(self,function,args,kwargs):
		self.function	= pickle.loads(pickle.dumps(function))
		self.args		= pickle.loads(pickle.dumps(args))
		self.kwargs		= pickle.loads(pickle.dumps(kwargs))
		
	def run(self):		
		for d in iter(self.iQ.get, None):
			self.oQ.put( self.function(d,*self.args,**self.kwargs) )

class Parallelizer():
	def __init__(self,threads=None):
		self.in_Queue = multiprocessing.Queue()
		self.out_Queue = multiprocessing.Queue()
	
		if threads == None or threads < 1:
			threads = multiprocessing.cpu_count()
		self.workers = [None]*threads
	
	def start(self):
		# Awful bug: tkFileDialog rewrites sys.frozen to dll
		# This causes multiprocessing.threading in Windows to barf due to malformed interpreter i.e. "Unknown Option --")
		# FORCE it back for now until I figure out a saner way to do this
		if getattr(sys,'frozen',False) == 'dll':
			sys.frozen = False
		
		for w in self.workers:
			w.start()
			
	def put(self,data):
		for d in data:
			self.in_Queue.put(d)
			
	def get(self):
		ret = []
		while not self.out_Queue.empty():
			ret.append( self.out_Queue.get() )
		return ret
	
	def abort(self):
		for w in self.workers:
			w.terminate()
		for w in self.workers:
			w.join()
			
	def stop(self):			
		for w in self.workers:
			self.in_Queue.put(None)
		for w in self.workers:
			w.join()
			
	def status(self):
		for w in self.workers:
			if w.returncode != 0:
				return False
		return True
						
class FunctionParallelizer(Parallelizer):
	def __init__(self,function,args=[],kwargs={},threads=None):
		Parallelizer.__init__(self,threads)

		for i in range(len(self.workers)):
			self.workers[i] = FunctionWorker(self.in_Queue,self.out_Queue)
		for w in self.workers:
			w.setup(function,args,kwargs)
			
		self.start()

class PluginParallelizer(Parallelizer):
	def __init__(self,plugin,threads=None):
		Parallelizer.__init__(self,threads)
		self.plugin = plugin
		self.plugin_class = plugin.__class__

		for i in range(len(self.workers)):
			self.workers[i] = self.plugin_class()
			self.workers[i].connect(self.plugin,self.in_Queue,self.out_Queue)
		
		self.start()
		
	def abort(self):
		for w in self.workers:
			w.terminate()
		for w in self.workers:
			w.join()
		self.plugin.close(abort=True)
			
	def stop(self):
		for w in self.workers:
			self.in_Queue.put(None)
		for w in self.workers:
			w.join()
		self.plugin.close(abort=False)

	