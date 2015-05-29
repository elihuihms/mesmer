import os
import shelve
import tempfile
import uuid
import argparse

from exceptions import *

class mesPluginBasic:

	def __init__( self, args ):
		self.name = ''
		self.version = ''
		self.info = ''
		self.path = None
		self.type = ('NONE')

		self.target_parser = argparse.ArgumentParser(prog=self.type[0])
		self.component_parser = argparse.ArgumentParser(prog=self.type[0])

	def close( self ):
		pass

	def info( self ):
		print "HELP for plugin: \"%s\"" % self.name
		print "\tVersion: %s" % self.version
		print "\tValid data types:"
		for t in self.type:
			print "\t\t%s" % t
		print ""
		print "Target file argument help:"
		try:
			self.target_parser.print_help()
		except:
			raise mesPluginError("Could not display target argument help for parser \"%s\"" % self.name)
		print ""
		print "Component file argument help:"
		try:
			self.component_parser.print_help()
		except:
			raise mesPluginError("Could not display component argument help for parser \"%s\"" % self.name)

	# base type stubs

	def ensemble_state( self, restraint, target_data , ensembles, file_path):
		return []

	def load_restraint( self, restraint, block, target_data ):
		return []

	def load_attribute( self, attribute, block, ensemble_data ):
		return []

	def load_bootstrap( self, bootstrap, restraint, ensemble_data, target_data ):
		return []

	def calc_fitness( self, restraint, target_data, ensemble_data, attributes, ratios ):
		return None

class mesPluginDB( mesPluginBasic ):

	def __init__( self, args ):
		mesPluginBasic.__init__( self, args )

		if( args.scratch ):
			self._db_path = os.path.join(args.scratch,uuid.uuid1().hex)
		else:
			self._db_path = os.path.join(tempfile.gettempdir(),uuid.uuid1().hex)
			
		try:
			self._db_handle = shelve.open(self._db_path,'c')
		except:
			raise mesPluginError("Could not create temporary scratch DB to store component data: \"%s\"" % self._db_path)
			
		# some db implementations append a .db to the provided path
		if( os.path.exists("%s%s" % (self._db_path,'.db')) ):
			self._db_path = "%s%s" % (self._db_path,'.db')

	def __del__( self ):
		try:
			if (self._db_handle != None):
				self._db_handle.close()

			if (self._db_path != None):
				os.unlink(self._db_path)
		except AttributeError:
			pass

	def put( self, data, key=None ):
		if( key == None ):
			key = uuid.uuid1().hex
		self._db_handle[key] = data
		return key

	def get( self, key ):
		return self._db_handle[key]