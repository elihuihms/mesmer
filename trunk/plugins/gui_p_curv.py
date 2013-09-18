import os
import argparse

from subprocess			import Popen

from gui.plugin_objects import guiPlotPlugin
from gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self, path):
		self.name = 'SAXS - Crysol'
		self.version = '2013.09.17'
		self.types = ('CURV','CURV0','CURV1','CURV2','CURV3','CURV4','CURV5','CURV6','CURV7','CURV8','CURV9')
		self.parser = None
		self.prog = os.path.join( path, 'utilities', 'make_curv_plot' )

	def plot(self, path):
		Popen([self.prog, path])
