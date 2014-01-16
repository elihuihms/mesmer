import os
import sys
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self):
		self.name = 'SAXS Plotter'
		self.version = '2014.01.15'
		self.types = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')
		self.parser = None
		
		# check the script local to the installation first, otherwise use what's in the system's path
		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_saxs_plot.py')
		if( not os.access(self.exe, os.R_OK) ):
			raise Exception("Could not read %s" % (self.exe) )

	def plot(self, path):
		Popen([sys.executable, self.exe, path])
