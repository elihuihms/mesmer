import argparse

from multiprocessing import Process

from exceptions import *

class guiCalcPlugin(Process):
	"""A class primitive for plugins used to calculate attributes from PDBs in the MESMER GUI

	This class extends a Process, permitting multithreading of plugin methods
	Since the plugin only needs to be set up once, after the setup() method is run on the parent plugin instance, the parent state is shared amongst the other plugin instances via connect()
	
	Attributes:
		name (string): (Required) Brief name of the plugin
		version (string): (Required) Version string of the plugin
		info (string): (Required) User-friendly information about the plugin
		type (string): (Required) e.g. "CURV" or "SAXS", etc.: the data type that this plugin will generate
		parser (Argparse parser): Argument parser for user-selectable options
		path (string): (Optional) Path to a required external executable or library

	"""
	
	def __init__(self):
		super(guiCalcPlugin, self).__init__()
		self.daemon = True
		self.iQ,self.oQ = None,None
		
		self.name = ''
		self.version = ''
		self.type = 'NONE'
		self.info = ''
		self.path = None
		self.parser = argparse.ArgumentParser(prog=self.name)

	def setup(self, window, options, outputpath):
		"""Set up the plugin, is called once before the plugin is then distributed for multithreading.
		
		Args:
			window (tk.Frame): Calling window, used for appropriately locating file dialog calls.
			options (dict): Dictionary containing any argument options obtained from the options window.
			outputpath (string): Directory that has been created where the output files are to be written.
		
		Returns:
			True on success, False on failure
			
		Exceptions:
			Raises mesPluginError on an exception
			
		"""

		self.outputpath	= outputpath
		self.options	= options
		
		return True
		
	def connect(self, parent, in_queue, out_queue):
		"""Connect to the provided Queues
		
		Input queue format: is sent None when processing is complete
		Output queue format: tuple of Error,(PDB,Info) where:
			Error (bool): Has an error occurred or not
			PDB (string): Current PDB path
			Info (variable): If Error is True, should contain some information describing the problem, otherwise can be None
			
		Args:
			parent (guiCalcPlugin): Parent plugin instance to obtain attributes from
			in_queue (multiprocessing.Queue): Queue containing incoming list of pdbs
			out_queue (multiprocessing.Queue): Queue to submit completed jobs (see Output queue format above)
			
		Returns: None
		"""
		self.__dict__.update(parent.__dict__)
		self.iQ,self.oQ = in_queue,out_queue
		
	def run(self):
		"""Start consuming PDBs from the input queue by calling the calculate() method repeatedly."""
		for d in iter(self.iQ.get, None):
			self.oQ.put( self.calculate(d) )

	def calculate(self, pdb):
		"""Calculate predicted data from the provided pdb.
		
		Args:
			pdb (string): Path to the pdb to calculate the output data from.
		
		Returns:
			Tuple of Error,(pdb,Explanation) (Boolean,(String,String))
			
		Exceptions:
			None, since this function will be split into a separate thread
		"""
		
		return True,(pdb,'Invalid Plugin')
		
	def close(self, abort=False):
		"""Shut the plugin down.
		
		Should close any open handles, remove temp files, etc.
		
		Args:
			abort (bool): Was calculation aborted before all PDBs were finished processing?
		
		Returns:
			True on success, False on failure
		
		Exceptions:
			Raises mesPluginError on an exception
		"""
		return True

class guiPlotPlugin():
	"""A class primitive for MESMER GUI plugins for generating figures depicting experimental data and MESMER's fits
		
	Attributes:
		name (string): (Required) Brief name of the plugin
		version (string): (Required) Version string of the plugin
		info (string): (Required) User-friendly information about the plugin
		type (tuple): (Required) Strings (e.g. "CURV", "SAXS") naming data types that this plugin can comprehend
		parser (Argparse parser): Argument parser for user-selectable options
		path (string): (Optional) Path to a required external executable or library
	"""

	def __init__(self):
		self.name = ''
		self.version = ''
		self.type = ('NONE')
		self.info = ''
		self.path = None #path to executable, if applicable
		self.parser = argparse.ArgumentParser(prog=self.name)

	def plot(self, path, options=None):
		"""Generate a figure from the provided path to a MESMER restraint fit file
		
		Args:
			path (string): Path to a MESMER restraint fit file corresponding to the plugin type
			options (dict): (Optional, defaults to None): Options set by the user based on the plugin's argument parser
		
		Return: True on success, False on failure
		
		Raises:
			Any exception that prevents the generation of the figure will be caught and displayed to the user.
		"""
		return True

