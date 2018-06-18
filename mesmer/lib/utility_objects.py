import sys
import argparse

from utility_functions	import print_msg
from plugin_objects		import MESMERPlugin

class MESMERUtility(MESMERPlugin):
	"""Basic MESMER utility - MESMER utilities can either be a separate executable (when installed and run from the CLI), or can be called from the GUI
	"""
	
	def __init__(self):
		super(MESMERUtility, self).__init__()
		self.parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
	
	def run(self,args):
		raise NotImplementedError("Valid MESMER Utilities should overwrite this dummy method")
		return errno,msg
	
	def exe(self):
		self.strip_parser_tags()
		
		ret = self.run(self.parser.parse_args())
		if ret == 0 or ret is None:
			sys.exit(0)
		else:
			errno,msg = ret # warning or error
			sys.exit(errno)
			