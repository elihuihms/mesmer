#!/usr/bin/env python

import sys

def run():
	try:
		import Tkinter as tk
		import tkMessageBox
	except ImportError:
		print "Failed on Tk import. Exiting"
		sys.exit()

	try:
		import argparse
	except ImportError:
		tkMessageBox.showerror("Error","Argparse module not installed")
		sys.exit()

	try:
		from lib.gui.win_main		import MainWindow
	except ImportError as e:
		tkMessageBox.showerror("Error","Error loading MESMER: %s" % (e))
		sys.exit()

	if( sys.version_info < (2,5) ):
		tkMessageBox.showerror("Error","Python version must be 2.5 or greater")
		sys.exit()

	root = tk.Tk()
	app = MainWindow(root)
	app.mainloop()

if( __name__ == "__main__" ):
	run()

