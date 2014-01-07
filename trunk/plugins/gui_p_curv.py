import os
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self, path):
		self.name = 'CURV Plotter'
		self.version = '2013.09.17'
		self.types = (
			'CURV','CURV0','CURV1','CURV2','CURV3','CURV4','CURV5','CURV6','CURV7','CURV8','CURV9',
			'DEER','DEER0','DEER1','DEER2','DEER3','DEER4','DEER5','DEER6','DEER7','DEER8','DEER9')
		self.parser = None
		self.prog = os.path.join( path, 'utilities', 'make_curv_plot.py' )

	def plot(self, path):
		Popen([self.prog, path])
