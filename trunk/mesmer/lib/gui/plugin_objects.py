import argparse

class guiCalcPlugin():
	def __init__(self):
		self.name = ''
		self.version = ''
		self.type = 'None'
		self.parser = argparse.ArgumentParser(prog=self.name)
		self.respawn = 1000 #ms b/t calculator calls

	def setup(self, pdbs, dir, options, threads):
		"""
		Sets up the plugin to calculate predicted data from a list of pdbs. The dir is already created and ready to receive the list of files
		"""

		self.pdbs = pdbs
		self.dir = dir
		self.options = options

	def calculator(self):
		"""
		Calculates predicted data from the list of pdbs provided to the plugin.
		Function is repeatedly called by the window every 100ms or so.

		"""

		raise Exception('Invalid Plugin')

		return 0

	def cancel(self):
		"""
		Called by the parent window when a run is cancelled before finishing.
		"""
		pass

	def close(self):
		pass

	def __del__(self):
		pass

class guiPlotPlugin():
	def __init__(self):
		self.name = ''
		self.version = ''
		self.types = ()
		self.parser = argparse.ArgumentParser(prog=self.name)

	def plot(self, path, options=None):
		pass
		
class Bunch(object):
	def __init__(self, dict):
		self.__dict__.update(dict)



