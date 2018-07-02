import os
import shelve
import logging
import multiprocessing

from mesmer.errors import *

_CONSOLE_OUTPUT = True
_CONSOLE_FORMAT = '%(levelname)s: %(message)s'
_CONSOLE_LEVEL = logging.INFO

_LOG_FILE_OUTPUT = True
_LOG_FILE_FORMAT = '%(levelname)s: %(message)s'
_LOG_FILE_LEVEL = logging.INFO
_LOG_FILE_TITLE = "mesmer_log.txt"

_LOG_DATA_TITLE = "mesmer_log.db"

class MesmerLogger(logging.getLoggerClass()):
	def __init__(self, *args, **kwargs):
		super(MesmerLogger, self).__init__(*args,**kwargs)
		self.db = None
		self.fp = None
		#self.queue = None

	def set_fp(self, path, mode='w'):
		if self.fp is None and _LOG_FILE_OUTPUT:
			self.fp = path
			
			chfmt = logging.Formatter(_LOG_FILE_FORMAT)

			ch = logging.FileHandler(self.fp, mode)
			ch.setLevel(_LOG_FILE_LEVEL)
			ch.setFormatter(chfmt)

			self.addHandler(ch)

	def set_db(self, shelf):
		if self.db is None:
			self.db = shelf

	def set_queue(self, queue):
		if self.queue is None:
			self.queue = queue

	def shutdown(self, *args, **kwargs):
#		super(MesmerLogger, self).shutdown(*args,**kwargs)
		
		if self.db is not None:
			self.db.sync()
			self.db.close()

def Logger():
	ret = MesmerLogger('MESMER')
	
	ret.setLevel(logging.DEBUG)
	
	#ret.set_queue(multiprocessing.Queue())

	if _CONSOLE_OUTPUT:
		chfmt = logging.Formatter(_CONSOLE_FORMAT)

		ch = logging.StreamHandler()
		ch.setLevel(_CONSOLE_LEVEL)
		ch.setFormatter(chfmt)

		ret.addHandler(ch)

	return ret

def open_results_dir( logger, arguments ):
	"""
	Creates a directory in which to save MESMER output files, and copies the parameters file into it
	"""

	ret = os.path.join( os.path.abspath(arguments.dir), arguments.name)

	if os.path.exists(ret):
		if arguments.force:
			logger.warn("Overwriting old result directory \"%s\"." % (ret))
			
			try:
				shutil.rmtree(ret)
			except OSError:
				logger.error("Could not delete directory \"%s\"." % (ret))
				return None
		else:
			logger.error("MESMER results directory \"%s\" already exists." % (ret))
			return None
	else:

		try:
			os.mkdir(ret)
		except OSError:
			logger.error("Couldn't create MESMER results directory \"%s\"." % (ret))
			return None

	try:
		logger.set_fp( os.path.join(ret,_LOG_FILE_TITLE) )
	except OSError:
		logger.error("Couldn't open MESMER results database file in \"%s\"."%(ret))
		return None

	try:
		db = shelve.open( os.path.join(ret,_LOG_DATA_TITLE) )
		logger.set_db(db)
		logger.db['args'] = arguments
	except OSError:
		logger.error("Couldn't open MESMER results database file in \"%s\"."%(ret))
		return None

	return ret
