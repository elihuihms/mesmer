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
			
#class ObjectWorker(multiprocessing.Process):
#	def __init__(self,in_queue,out_queue,object,function_name):
#		"""This a pretty horrible hack, it basically converts an object to a process, and then feeds elements from the input to function_name()"""
#		super(ObjectWorker, self).__init__()
#		self.iQ,self.oQ = in_queue,out_queue
#		self.daemon = True
#		
#		self.__dict__.update(copy.deepcopy(object.__dict__))
#		for k,v in object.__dict__.items():
#			self.__dict__[k] = copy.deepcopy(v)
#		self._function = getattr( object, function_name )
#				
#	def run(self):
#		for d in iter(self.iQ.get, None):
#			self.oQ.put( self._function( d ) )

class Parallelizer():
	def __init__(self,threads=None):
		self.in_Queue = multiprocessing.Queue()
		self.out_Queue = multiprocessing.Queue()
	
		if threads == None or threads < 1:
			threads = multiprocessing.cpu_count()
		self.workers = [None]*threads
	
	def start(self):
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

	