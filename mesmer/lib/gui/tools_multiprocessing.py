import multiprocessing

class Worker(multiprocessing.Process):
	def __init__(self,in_queue,out_queue):
		super(Worker, self).__init__()
		self.iQ = in_queue
		self.oQ = out_queue
		self.daemon = True
		
	def setup(self,function,args,kwargs):
		try:
			import cPickle as pickle
		except:
			import pickle

		# arguments have to picklable!
		pickle.dumps(function)
		pickle.dumps(args)
		pickle.dumps(kwargs)
		
		self.function = function
		self.args = args
		self.kwargs = kwargs
		
	def run(self):		
		for d in iter(self.iQ.get, None):
			self.oQ.put( self.function(d,*self.args,**self.kwargs) )
			
class Parallelizor():
	def __init__(self,function,args=[],kwargs={},threads=1):
		self.in_Queue = multiprocessing.Queue()
		self.out_Queue = multiprocessing.Queue()
		self.workers = [None]*threads

		for i in xrange(threads):
			self.workers[i] = Worker(self.in_Queue,self.out_Queue)
			self.workers[i].setup(function,args,kwargs)
			self.workers[i].start()	
	
	def put(self,data):
		for d in data:
			self.in_Queue.put(d)
			
	def get(self):
		ret = []
		while not self.out_Queue.empty():
			ret.append( self.out_Queue.get() )
		return ret
	
	def abort(self):
		# clear the queue
		for w in self.workers:
			w.terminate()

	def stop(self):			
		for w in self.workers:
			self.in_Queue.put(None)
		for w in self.workers:
			w.join()