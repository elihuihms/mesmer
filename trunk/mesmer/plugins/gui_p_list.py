import os
import sys
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeListFromOptions

class plugin(guiPlotPlugin):

	def __init__(self):
		self.name = 'LIST/TABL Plotter'
		self.version = '2014.01.15'
		self.types = (
			'LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9',
			'TABL','TABL0','TABL1','TABL2','TABL3','TABL4','TABL5','TABL6','TABL7','TABL8','TABL9')

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-xCol',	default=1,		type=int,	help='The column containing the desired component attribute')
		self.parser.add_argument('-yCol',	default=2,		type=int,	help='The column to use as y-axis data')

		# check the script local to the installation first, otherwise use what's in the system's path
		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_list_plot.py')
		if( not os.access(self.exe, os.R_OK) ):
			raise Exception("Could not read %s" % (self.exe) )

	def plot(self, path, options):
		cmd = [sys.executable, self.exe, path]
		cmd.extend( makeListFromOptions(options) )
		Popen(cmd)
