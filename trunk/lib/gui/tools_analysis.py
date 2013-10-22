import os
import Tkinter as tk
import tkMessageBox

from win_log	import LogWindow

def openRunDir( w, path ):

	p1 = os.path.join(path,'mesmer_log.db')
	p2 = os.path.join(path,'mesmer_log.db.db') # some DB schemes do this

	if(not os.path.exists(p1) and not os.path.exists(p2)):
		tkMessageBox.showerror("Error","Could not find MESMER results DB in \"%s\"" % path,parent=w)
		return

	w.path = path
	w.resultsDBPath = p1

	w.activeDir.set(path)
	w.updateGenerationList()
	w.currentSelection = [None,None,None]
	w.openLogButton.config(state=tk.NORMAL)
	w.statusText.set('Opened existing run')

	openLogWindow( w, path )
	return

def openLogWindow( w, path=False ):

	if(w.logWindowMaster == None or not w.logWindowMaster.winfo_exists()):
		w.logWindowMaster = tk.Toplevel(w.master)
		w.logWindow = LogWindow(w.logWindowMaster)
	else:
		w.logWindow.logText.delete(1.0,tk.END) # clear the log text

	if(path):
		w.logWindow.updateLog( os.path.join(path,'mesmer_log.txt') ) # load log from file
	else:
		w.logWindow.cancelButton.config(state=tk.DISABLED)
		w.openLogButton.config(state=tk.DISABLED)

	w.logWindowMaster.lower( w.master )
	return