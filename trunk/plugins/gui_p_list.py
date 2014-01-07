import os
import argparse

from subprocess				import Popen

from lib.gui.plugin_objects import guiPlotPlugin
from lib.gui.tools_plugin	import makeStringFromOptions

class plugin(guiPlotPlugin):

	def __init__(self, path):
		self.name = 'LIST/TABL Plotter'
		self.version = '2013.10.22'
		self.types = (
			'LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9',
			'TABL','TABL0','TABL1','TABL2','TABL3','TABL4','TABL5','TABL6','TABL7','TABL8','TABL9')

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-xCol',	default=1,		type=int,	help='The column containing the desired component attribute')
		self.parser.add_argument('-yCol',	default=2,		type=int,	help='The column to use as y-axis data')

		self.prog = os.path.join( path, 'utilities', 'make_list_plot.py' )

	def plot(self, path, options):
		cmd = [self.prog]
		cmd.extend( makeStringFromOptions(options).split() )
		cmd.append( path )
		Popen(cmd)
