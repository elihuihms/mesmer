import os
import shelve
import Tkinter as tk
import tkFileDialog
import tkMessageBox

from threading		import Thread
from Queue			import Queue, Empty

from gui.win_options	import OptionsWindow
from gui.tools_run	import *

def openRunDir( w, path ):

	p1 = os.path.join(path,'mesmer_log.db')
	p2 = os.path.join(path,'mesmer_log.db.db') # some DB schemes do this

	if(not os.path.exists(p1) and not os.path.exists(p2)):
		tkMessageBox.showerror("Error","Could not find MESMER results DB in \"%s\"" % path,parent=w)
		return

	w.resultsDBPath = p1

	w.activeDir.set(path)
	w.currentSelection = [None,None,None]
	w.openLogWindow()
	w.openLogButton.config(state=tk.NORMAL)
	updateGenerationList(w, path)
	w.statusText.set('Opened existing run')

def updateGenerationList( w, path ):
	try:
		w.resultsDB = shelve.open( w.resultsDBPath, 'r' )
	except:
		return # perhaps a concurrent read/write on an older DB implementation (10.6, I'm lookin' at you)

	# append new generations to the list
	if(w.resultsDB.has_key('ensemble_stats')):
		for i in range(w.generationsList.size(),len(w.resultsDB['ensemble_stats'])):
			string = "%s%s%s%s" % (
			"%05i".ljust(14) % i,
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i]['total'][0],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i]['total'][1],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][i]['total'][2]
			)
			w.generationsList.insert(tk.END, string )
	return

def setGenerationSel( w, evt=None ):
	if(len(w.generationsList.curselection())<1):
		return
	w.currentSelection[0] = int(w.generationsList.curselection()[0])

	w.targetsList.delete(0, tk.END)
	for name in w.resultsDB['ensemble_stats'][w.currentSelection[0] ]['target']:
		string = "%s%s%s%s" % (
			name[:14].ljust(14),
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][ w.currentSelection[0] ]['target'][name][0],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][ w.currentSelection[0] ]['target'][name][1],
			"%.3e".ljust(6) % w.resultsDB['ensemble_stats'][ w.currentSelection[0] ]['target'][name][2]
			)
		w.targetsList.insert(tk.END, string )

	w.targetsList.selection_set(0)
	w.targetsList.see(0)
	setTargetSel( w )
	setWidgetAvailibility( w )

def setTargetSel( w, evt=None ):
	if(len(w.targetsList.curselection())<1):
		return

	for (i,name) in enumerate(w.resultsDB['ensemble_stats'][ w.currentSelection[0] ]['target'].keys()):
		if(i == int(w.targetsList.curselection()[0])):
			w.currentSelection[1] = name

	w.restraintsList.delete(0, tk.END)
	for type in w.resultsDB['restraint_stats'][ w.currentSelection[0] ]:
		if(type == 'Total'):
			break
		string = "%s%s%s%s" % (
		type.ljust(14),
		"%.3e".ljust(6) % w.resultsDB['restraint_stats'][ w.currentSelection[0] ][type][ w.currentSelection[1] ][0],
		"%.3e".ljust(6) % w.resultsDB['restraint_stats'][ w.currentSelection[0] ][type][ w.currentSelection[1] ][1],
		"%.3e".ljust(6) % w.resultsDB['restraint_stats'][ w.currentSelection[0] ][type][ w.currentSelection[1] ][2]
		)
		w.restraintsList.insert(tk.END, string )

	w.restraintsList.selection_set(0)
	w.restraintsList.see(0)
	setRestraintSel( w )
	setWidgetAvailibility( w )

def setRestraintSel( w,evt=None ):
	if(len(w.restraintsList.curselection())<1):
		return

	for (i,type) in enumerate(w.resultsDB['restraint_stats'][ w.currentSelection[0] ].keys()):
		if(i == int(w.restraintsList.curselection()[0])):
			w.currentSelection[2] = type

	path = (os.path.join(w.activeDir.get(), 'restraints_%s_%s_%05i.out' % (w.currentSelection[1],w.currentSelection[2],int(w.currentSelection[0]))))
	if(os.path.exists(path)):
		w.fitPlotButton.config(state=tk.NORMAL)
	else:
		w.fitPlotButton.config(state=tk.DISABLED)

def setWidgetAvailibility( w ):
	if( w.currentSelection[0] == None):
		w.histogramPlotButton.config(state=tk.DISABLED)
	else:
		w.histogramPlotButton.config(state=tk.NORMAL)

	if( w.currentSelection[0] == None or w.currentSelection[1] == None ):
		w.correlationPlotButton.config(state=tk.DISABLED)
		w.writePDBsButton.config(state=tk.DISABLED)
	else:
		w.correlationPlotButton.config(state=tk.NORMAL)
		w.writePDBsButton.config(state=tk.NORMAL)

	if( w.currentSelection[0] == None or w.currentSelection[1] == None or w.attributeTable.get() == ''):
		w.attributePlotButton.config(state=tk.DISABLED)
		w.attributePlotButton.config(state=tk.DISABLED)
	else:
		w.attributePlotButton.config(state=tk.NORMAL)
		w.attributePlotButton.config(state=tk.NORMAL)






