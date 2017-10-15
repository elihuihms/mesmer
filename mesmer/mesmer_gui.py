#!/usr/bin/env python

# MESMER - Minimal Ensemble Solutions to Multiple Experimental Restraints
# Copyright (C) 2017 SteelSnowflake Software LLC
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import sys

from lib.exceptions			import *
from lib.setup_functions	import open_user_prefs

def run():
	
	try:
		import Tkinter as tk
		import tkMessageBox
	except ImportError:
		print "The MESMER GUI requires the Tk/Tcl library."
		sys.exit(1)

	if( sys.version_info < (2,6) ):
		tkMessageBox.showerror("Error","Python version must be 2.6 or greater")
		sys.exit(1)

	try:
		shelf = open_user_prefs( mode='c' )
	except mesSetupError as e:
		tkMessageBox.showerror("Error","Error loading MESMER preferences: %s"%(e))
		sys.exit(1)
	except:
		tkMessageBox.showerror("Error","Could not update MESMER preferences file. Perhaps your user folder is read-only?")
		sys.exit(1)
		
	try:
		from lib.gui.win_main import MainWindow
	except ImportError as e:
		tkMessageBox.showerror("Error","Error loading MESMER: %s" % (e))
		sys.exit(1)

	root = tk.Tk()
	if sys.platform == 'darwin':
		os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
	
	app = MainWindow(root)	
	app.mainloop()
	
	sys.exit(0)

if( __name__ == "__main__" ):
	run()
