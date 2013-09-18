import os
import time
import shutil
import Tkinter as tk
import tkMessageBox

from subprocess			import Popen,PIPE,STDOUT

from gui.tools_setup	import makeMESMERArgsFromWindow,makeStringFromArgs
from gui.tools_analysis	import *
from gui.win_analysis	import AnalysisWindow

def startRun( w, mesmerPath ):

	args = makeMESMERArgsFromWindow(w)

	path = os.path.join(args.dir,args.name)
	if(os.path.exists(path)):
		result = tkMessageBox.askyesno('Warning',"Continuing will overwrite an existing run folder, continue anyway?",parent=w)
		if(result):
			try:
				shutil.rmtree(path)
			except OSError:
				tkMessageBox.showerror("Error","ERROR: Couldn't remove \"%s\"" % path,parent=w)
				return False
		else:
			return False

	if(not os.path.isfile(mesmerPath) or not os.access(mesmerPath, os.X_OK) ):
		tkMessageBox.showerror("Error","Error accessing MESMER executable at \"%s\"" % mesmerPath,parent=w)
		return False

	path = os.path.join(args.dir,"%s_args.txt" % args.name)
	f = open( path, 'w' )
	f.write(makeStringFromArgs(args))
	f.close()

	try:
		pHandle = Popen( [mesmerPath,"@%s" % path], cwd=args.dir, stdout=PIPE, stderr=STDOUT )
	except OSError as e:
		tkMessageBox.showerror("Error","Error starting a MESMER run.\nError:\n%s" % e,parent=w)
		return False

	time.sleep(1) # sleep a second to get any MESMER arg parsing errors
	pHandle.poll()
	if(pHandle.returncode != None):
		tkMessageBox.showerror("Error","Error starting a MESMER run.\nError:\n%s" % pHandle.stdout.read(),parent=w)
		return False

	# w.parent = MainWindow
	w.parent.masters.append( tk.Toplevel(w.parent.master) )
	w.parent.windows.append( AnalysisWindow(w.parent.masters[-1],os.path.join(args.dir,args.name),pHandle) )

	return True

def connectToRun( w, path, pHandle ):

	p1 = os.path.join(path,'mesmer_log.db')
	p2 = os.path.join(path,'mesmer_log.db.db')

	if(w.connectCounter > 10): # try for ten seconds to find the mesmer results DB
		tkMessageBox.showerror("Error","Could not find MESMER results DB in \"%s\". Perhaps MESMER crashed?" % path,parent=w)
		return

	if(not os.path.exists(p1) and not os.path.exists(p2)):
		w.connectCounter+=1
		w.updateHandle = w.after( 1000, connectToRun, *(w,path,pHandle) )
		return

	w.resultsDBPath = p1

	try:
		w.resultsDB = shelve.open( w.resultsDBPath, 'r' )
	except:
		tkMessageBox.showerror("Error","Error loading the MESMER log database from \"%s\"." % path,parent=w)
		return

	w.activeDir.set(path)
	w.currentSelection = [None,None,None]

	def getMESMEROutput( out, queue ):
		for line in iter(out.readline, b''):
			queue.put(line)
		out.close()

	w.MESMEROutput_Q = Queue()
	w.MESMEROutput_T = Thread(target=getMESMEROutput, args=(pHandle.stdout, w.MESMEROutput_Q))
	w.MESMEROutput_T.daemon = True
	w.MESMEROutput_T.start()

	w.openLogWindow( True )
	w.updateHandle = w.after( 1000, updateWindowResults, *(w,path,pHandle) )
	w.activeDirEntry.config(state=tk.DISABLED)
	w.activeDirButton.config(state=tk.DISABLED)

def updateWindowResults( w, path, pHandle ):

	pHandle.poll()
	if(pHandle.returncode == None):
		w.abortButton.config(state=tk.NORMAL)
	elif(pHandle.returncode == 0):
		w.abortButton.config(state=tk.DISABLED)
		w.statusText.set('Finished')
		updateLogWindow( w )
		return
	else:
		tkMessageBox.showerror("Error","MESMER exited with error code %i. Please check the output log for more information." % pHandle.returncode,parent=w)
		w.abortButton.config(state=tk.DISABLED)
		w.statusText.set('Error')
		updateLogWindow( w )
		return

	updateGenerationList( w, path )
	updateLogWindow( w )
	w.updateHandle = w.after( 1000, updateWindowResults, *(w,path,pHandle) )

	return

def updateLogWindow( w ):
	try:
		while(True):
			line = w.MESMEROutput_Q.get_nowait()
			if( 'Reading target file' in line):
				w.statusText.set('Reading targets...')
			elif( 'Component loading progress' in line):
				w.statusText.set('Loading components...')
			elif( 'Optimizing parent component ratios' in line):
				w.statusText.set('Optimizing component ratios...')
			elif( 'Optimizing offspring component ratios' in line):
				w.statusText.set('Optimizing component ratios...')
			elif( 'Calculating best fit statistics' in line):
				w.statusText.set('Finding best fit intervals...')

			if( "\r" in line ): #carriage return
				w.logWindow.logText.delete("%s.0" % w.logWindow.logText.index('end').split('.')[0]-1, tk.END)
			w.logWindow.logText.insert(tk.END,line)
	except:
		return