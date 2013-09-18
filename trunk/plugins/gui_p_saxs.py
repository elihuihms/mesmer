import os
import argparse

from subprocess			import Popen

from gui.plugin_objects import guiPlotPlugin
from gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self, path):
		self.version = '2013.09.17'
		self.types = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')
		self.parser = None
		self.prog = os.path.join( path, 'utilities', 'make_saxs_plot' )

	def plot(self, path):
		Popen([self.prog, path])
