#!/usr/bin/env python

import os
import re
import shelve
import Tkinter as tk
import tkFileDialog
import tkMessageBox

from subprocess		import Popen,PIPE

#from win_analysis	import AnalysisWindow

def startRun( mainWindow, mesmerPath, args ):

	if(not os.path.isfile(mesmerPath) or not os.access(mesmerPath, os.X_OK) ):
		tkMessageBox.showerror("Error","Error accessing MESMER executable at \"%s\"" % mesmerPath)
		return False

	mainWindow.masters.append( tk.Toplevel(mainWindow.master) )
	mainWindow.windows.append( AnalysisWindow(mainWindow.masters[-1],os.path.join(args.dir,args.name)) )

	return True

def makeCorrelationPlot( w ):
	p1 = os.path.join(w.activeDir.get(), 'component_correlations_%05i.tbl' % int(w.currentSelection[0]) )
	p2 = os.path.join(w.activeDir.get(), 'component_statistics_%s_%05i.tbl' % (w.currentSelection[1],int(w.currentSelection[0])) )
	if( os.path.isfile(p1) and os.path.isfile(p2) ):
		cmd = os.path.join(w.prefs['mesmer_util_path'],'make_correlation_plot')
		try:
			Popen([cmd,p1,p2,'-size','20'])
		except OSError:
			tkMessageBox.showerror("Error","Could not open the correlation plotter")
			return

def loadResultsLog( w, path ):
	try:
		w.resultsDB = shelve.open( os.path.join(path,'mesmer_log.db') )
	except:
		tkMessageBox.showerror("Error","Error loading the MESMER log database from the specified folder.")
		return
	generations = w.resultsDB.keys()
	generations.remove('args')

	w.activeDir.set(path)

	w.generationsList.delete(0, tk.END)
	for g in generations:
		string = "%s\t\t\t%s\t%s\t%s" % (
			"%05i" % int(g),
			"%.3e" % w.resultsDB[g][0]['total'][0],
			"%.3e" % w.resultsDB[g][0]['total'][1],
			"%.3e" % w.resultsDB[g][0]['total'][2]
			)
		w.generationsList.insert(tk.END, string )

	# set initial selections
	w.currentSelection = [None,None,None]
	w.generationsList.selection_set(0)
	w.generationsList.see(0)
	setGenerationSel( w )
	w.targetsList.selection_set(0)
	w.targetsList.see(0)
	setTargetSel( w )
	w.restraintsList.selection_set(0)
	w.restraintsList.see(0)
	setRestraintSel( w )

	w.updateWidgets()

def setWidgetAvailibility( w, generation ):
	if(os.path.isfile( os.path.join(w.activeDir.get(), 'component_statistics_%05i.tbl' % generation) )):
		w.attributePlotButton.config(state=tk.NORMAL)
		if(w.attributeTable.get() != ''):
			w.attributePlotButton.config(state=tk.NORMAL)
		else:
			w.attributePlotButton.config(state=tk.DISABLED)
	else:
		w.attributePlotButton.config(state=tk.DISABLED)
		w.attributePlotButton.config(state=tk.DISABLED)

	if(os.path.isfile( os.path.join(w.activeDir.get(), 'component_correlations_%05i.tbl' % generation) )):
		w.correlationPlotButton.config(state=tk.NORMAL)
	else:
		w.correlationPlotButton.config(state=tk.DISABLED)

def setGenerationSel( w, evt=None ):
	w.currentSelection[0] = str(w.generationsList.curselection()[0])

	w.targetsList.delete(0, tk.END)
	for name in w.resultsDB[ w.currentSelection[0] ][0]['target']:
		string = "%s\t%s\t%s\t%s" % (
			name[:16].ljust(16),
			"%.3e" % w.resultsDB[ w.currentSelection[0] ][0]['target'][name][0],
			"%.3e" % w.resultsDB[ w.currentSelection[0] ][0]['target'][name][1],
			"%.3e" % w.resultsDB[ w.currentSelection[0] ][0]['target'][name][2]
			)
		w.targetsList.insert(tk.END, string )

	#setWidgetAvailibility( w, int(w.currentSelection[0]) )

def setTargetSel( w, evt=None ):
	for (i,name) in enumerate(w.resultsDB[ w.currentSelection[0] ][0]['target'].keys()):
		if(i == int(w.targetsList.curselection()[0])):
			w.currentSelection[1] = name

	w.restraintsList.delete(0, tk.END)
	for type in w.resultsDB[ w.currentSelection[0] ][1]:
		if(type == 'Total'):
			break
		string = "%s\t%s\t%s\t%s" % (
		type.ljust(16),
		"%.3e" % w.resultsDB[ w.currentSelection[0] ][1][type][ w.currentSelection[1] ][0],
		"%.3e" % w.resultsDB[ w.currentSelection[0] ][1][type][ w.currentSelection[1] ][1],
		"%.3e" % w.resultsDB[ w.currentSelection[0] ][1][type][ w.currentSelection[1] ][2]
		)
		w.restraintsList.insert(tk.END, string )

def setRestraintSel( w,evt=None ):
	for (i,type) in enumerate(w.resultsDB[w.currentSelection[0] ][1].keys()):
		if(i == int(w.restraintsList.curselection()[0])):
			w.currentSelection[2] = type





