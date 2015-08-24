import os
import sys
import argparse

from subprocess				import Popen

from lib.exceptions			import *
from lib.gui.plugin_objects import guiPlotPlugin

class plugin(guiPlotPlugin):

	def __init__(self):
		guiPlotPlugin.__init__(self)
		self.name = 'CURV Plotter'
		self.version = '2015.08.19'
		self.info = "This plugin generates an overlay plot of two continuous datasets."
		self.types = (
			'CURV','CURV0','CURV1','CURV2','CURV3','CURV4','CURV5','CURV6','CURV7','CURV8','CURV9',
			'DEER','DEER0','DEER1','DEER2','DEER3','DEER4','DEER5','DEER6','DEER7','DEER8','DEER9')
		self.parser = None

		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_curv_plot.py')
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