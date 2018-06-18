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
		import os
		os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
	
	app = MainWindow(root)	
	app.mainloop()
	
	sys.exit(0)