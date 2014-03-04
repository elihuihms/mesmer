import os
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self):
		self.name = 'SAXS Plotter'
		self.version = '2013.09.17'
		self.types = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')
		self.parser = None
		
		# check the script local to the installation first, otherwise use what's in the system's path
		tmp = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_saxs_plot.py')
		if( os.access(tmp, os.X_OK) ):
			self.prog = tmp
		else:
			self.prog = 'make_saxs_plot'

	def plot(self, path):
		Popen([self.prog, path])
