import os
import shelve
import Tkinter as tk
import tkMessageBox

from win_log	import LogWindow

def openRunDir( w, path ):

	p1 = os.path.join(path,'mesmer_log.db')
	p2 = os.path.join(path,'mesmer_log.db.db') # some DB schemes do this

	if not os.access(p1, os.R_OK) and not os.access(p2, os.R_OK):
		tkMessageBox.showerror("Error","Could not find a results DB in \"%s\"" % path,parent=w)
		return

	w.path = path
	w.resultsDBPath = p1
	w.activeDir.set(path)
	w.currentSelection = [None,None,None]
	w.openLogButton.config(state=tk.NORMAL)
	w.progressPlotButton.config(state=tk.NORMAL)
	w.statusText.set('Opened existing run')

	updateGenerationList( w )
	openLogWindow( w, path )
	return

def updateGenerationList( w ):

	try:
		w.resultsDB = shelve.open( w.resultsDBPath, 'r' )
	except Exception as e:
		w.master.config(cursor='')
		tkMessageBox.showerror("Error",'Error opening results DB: %s' % (e),parent=w)
		raise e

	# append new generations to the list
	if(w.resultsDB.has_key('ensemble_stats')):
		for i in range(w.generationsList.size(),len(w.resultsDB['ensemble_stats'])):
			string = "%s%s%s%s" % (
			"%05i".ljust(14) % i,
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i][0][0],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i][0][1],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i][0][2]
			)
			w.generationsList.insert(tk.END, string )

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