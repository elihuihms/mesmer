import os
import shelve
import tempfile
import uuid

class plugin_basic:

	name = ''
	version = ''
	types = ()

	def __init__( self, args ):
		pass

	def __del__( self ):
		pass

	def info():
		print "Plugin: \"%s\"" % self.name
		print "\tVersion: \"%s\"" % self.version
		print "\tData types:"
		for t in self.types:
			print "\t\t%s" % t

	# base type stubs

	def ensemble_state( self, restraint, target_data , ensembles, file_path):
		return (True,[])

	def load_restraint( self, restraint, block, target_data ):
		return (True,[])

	def load_attribute( self, attribute, block, ensemble_data ):
		return (True,[])

	def load_bootstrap( self, bootstrap, restraint, ensemble_data, target_data ):
		return (True,[])

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		return None

class plugin_db( plugin_basic ):

	def __init__( self, args ):

		self._db_path ="%s%s%s%s" % (tempfile.gettempdir(),os.sep,uuid.uuid1().hex,'.db')
		self._db_handle = shelve.open(self._db_path,'c')

		# some db implementations append a .db to the provided path
		if( os.path.exists("%s%s" % (self._db_path,'.db')) ):
			self._db_path = "%s%s" % (self._db_path,'.db')

		return None

	def __del__( self ):

		if (self._db_handle != None):
			self._db_handle.close()

		if (self._db_path != None):
			os.unlink(self._db_path)

		return None

	def put( self, data, key=None ):
		if( key == None ):
			key = uuid.uuid1().hex
		self._db_handle[key] = data
		return key

	def get( self, key ):
		return self._db_handle[key]