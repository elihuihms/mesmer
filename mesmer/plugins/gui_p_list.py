import os
import sys
import argparse

from subprocess				import Popen

from mesmer.lib.exceptions			import *
from mesmer.lib.plugin_functions	import list_from_parser_dict
from mesmer.lib.gui.plugin_objects	import guiPlotPlugin

class plugin(guiPlotPlugin):

	def __init__(self):
		guiPlotPlugin.__init__(self)
		self.name = 'LIST/TABL Plotter'
		self.version = '1.0.0'
		self.info = "This plugin generates a correlation plot between two discretely sampled datasets."
		self.types = (
			'LIST','LIST0','LIST1','LIST2','LIST3','LIST4','LIST5','LIST6','LIST7','LIST8','LIST9',
			'TABL','TABL0','TABL1','TABL2','TABL3','TABL4','TABL5','TABL6','TABL7','TABL8','TABL9')

		self.parser = argparse.ArgumentParser(prog=self.name)
		self.parser.add_argument('-xCol',	metavar='X column',	default=1,	type=int,	help='The column containing the desired component attribute')
		self.parser.add_argument('-yCol',	metavar='Y column',	default=2,	type=int,	help='The column to use as y-axis data')

		self.exe = os.path.join(os.path.dirname(os.path.dirname(__file__)),'utilities','make_list_plot.py')
		if( not os.access(self.exe, os.R_OK) ):
			raise mesPluginError("Could not access plotter utility located at \"%s\". Perhaps the MESMER directory is incorrectly set?"%(self.exe) )

	def plot(self, path, options, title):
		try:
			Popen([sys.executable, self.exe, path, '-title', title]+list_from_parser_dict(options))
		except Exception as e:
			if(e.errno == os.errno.ENOENT):
				raise mesPluginError("Could not execute plotter utility. Perhaps the MESMER directory is set incorrectly?")
			else:
				raise e

		return True