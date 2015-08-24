import os
import sys
import argparse

from subprocess				import Popen

from lib.exceptions			import *
from lib.gui.plugin_objects import guiPlotPlugin

class plugin(guiPlotPlugin):

	def __init__(self):
		guiPlotPlugin.__init__(self)
		self.name = 'SAXS Plotter'
		self.version = '1.0.0'
		self.info = "This plugin generates an overlay log-scaled plot of two SAXS datasets."
		self.types = ('SAXS','SAXS0','SAXS1','SAXS2','SAXS3','SAXS4','SAXS5','SAXS6','SAXS7','SAXS8','SAXS9')
		self.parser = None
		
		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_saxs_plot.py')
		if( not os.access(self.exe, os.R_OK) ):
			raise mesPluginError("Could not access plotter utility located at \"%s\". Perhaps the MESMER directory is incorrectly set?"%(self.exe) )

	def plot(self, path, options, title):
		try:
			Popen([sys.executable, self.exe, path, '-title', title])
		except Exception as e:
			if(e.errno == os.errno.ENOENT):
				raise mesPluginError("Could not execute plotter utility. Perhaps the MESMER directory is set incorrectly?")
			else:
				raise e
		
		return True
