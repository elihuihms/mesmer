import os
import sys
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self):
		self.name = 'CURV Plotter'
		self.version = '2014.01.15'
		self.types = (
			'CURV','CURV0','CURV1','CURV2','CURV3','CURV4','CURV5','CURV6','CURV7','CURV8','CURV9',
			'DEER','DEER0','DEER1','DEER2','DEER3','DEER4','DEER5','DEER6','DEER7','DEER8','DEER9')
		self.parser = None

		# check the script local to the installation first, otherwise use what's in the system's path
		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_curv_plot.py')
		if( not os.access(self.exe, os.R_OK) ):
			raise Exception("Could not read %s" % (self.exe) )

	def plot(self, path):
		Popen([sys.executable, self.exe, path])
