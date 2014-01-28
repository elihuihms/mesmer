import os
import sys
import shelve
import shutil
import time
import Tkinter as tk
import tkMessageBox

from subprocess		import Popen,PIPE,STDOUT
from threading		import Thread
from Queue			import Queue, Empty

from tools_setup	import makeMESMERArgsFromWindow,makeStringFromArgs
from tools_analysis	import openLogWindow,updateGenerationList
from win_analysis	import AnalysisWindow

def startRun( w ):

	args = makeMESMERArgsFromWindow(w) # w in this context is a SetupWindow

	path = os.path.join(args.dir,args.name)
	if(os.path.exists(path)):
		result = tkMessageBox.askyesno('Warning',"Continuing will overwrite an existing results folder, continue anyway?",parent=w)
		if(result):
			try:
				shutil.rmtree(path)
			except OSError:
				tkMessageBox.showerror("Error","ERROR: Couldn't remove \"%s\"" % path,parent=w)
				return False
		else:
			return False

	try:
		argpath = os.path.join(args.dir,"%s_args.txt" % args.name)
		f = open( argpath, 'w' )
		f.write(makeStringFromArgs(args))
		f.close()
	except Exception as e:
		tkMessageBox.showerror("Error","Could not write MESMER run configuration file: %s" % (e),parent=w)

	# fire up MESMER and get the process handle
	cmd = ['mesmer']
	if( w.prefs['mesmer_base_dir'] != '' ):
		cmd = [sys.executable,os.path.join(w.prefs['mesmer_base_dir'],'mesmer.py')]
	cmd.append("@%s" % argpath)

	try:
		pHandle = Popen( cmd, cwd=args.dir, stdout=PIPE, stderr=STDOUT, bufsize=0, universal_newlines=True )
	except OSError as e:
		tkMessageBox.showerror("Error","Error starting a MESMER run.\nError:\n%s" % e,parent=w)
		return False

	time.sleep(1) # sleep a second to catch any MESMER argument parsing errors
	if(pHandle.poll() != None):
		tkMessageBox.showerror("Error","Error starting a MESMER run.\nError:\n%s" % pHandle.stdout.read(),parent=w)
		return False

	# create analysis window, attach to original MainWindow, w.parent = MainWindow
	w.parent.masters.append( tk.Toplevel(w.parent.master) )
	w.parent.windows.append( AnalysisWindow(w.parent.masters[-1],os.path.join(args.dir,args.name),pHandle) )

	return True # tell setup window to close down now

def connectToRun( w, path, pHandle ):

	try: # instantiate the connection counter if necessary
		w.connectCounter+=1
	except:
		w.connectCounter = 0

	if(w.connectCounter > 60): # give up after a minute while trying to reach results DB
		tkMessageBox.showerror("Error","Could not find MESMER results DB in \"%s\". Perhaps MESMER crashed?" % path,parent=w)
		return

	try: # try for ten seconds to find results DB
		w.resultsDBPath = os.path.join(path,'mesmer_log.db')
		w.resultsDB = shelve.open( w.resultsDBPath, 'r' )
	except:
		w.updateHandle = w.after( 1000, connectToRun, *(w,path,pHandle) )
		return

	# update the analysis window
	w.activeDir.set(path)
	w.activeDirEntry.config(state=tk.DISABLED)
	w.activeDirButton.config(state=tk.DISABLED)
	w.currentSelection = [None,None,None]
	w.abortButton.config(state=tk.NORMAL)
	w.progressPlotButton.config(state=tk.NORMAL)

	def readQueue( out, queue ):
		for line in iter(out.readline, b''):
			queue.put(line)
		out.close()

	# create the logging queue and polling thread
	w.pHandle = pHandle
	w.pHandle_Q = Queue()
	w.pHandle_T = Thread(target=readQueue, args=(pHandle.stdout, w.pHandle_Q))
	w.pHandle_T.daemon = True
	w.pHandle_T.start()

	# open the log window
	openLogWindow( w )

	w.updateHandle = w.after( 1000, updateAnalysisWindow, w )
	return

def updateAnalysisWindow( w ):

	w.pHandle.poll()
	if(w.pHandle.returncode == None):
		w.updateHandle = w.after( 1000, updateAnalysisWindow, w )
		updateGenerationList( w )
		updateLogWindow( w )
		return
	elif(w.pHandle.returncode == 0):
		w.abortButton.config(state=tk.DISABLED)
		w.statusText.set('Finished')
		updateLogWindow( w )
		return
	else:
		tkMessageBox.showerror("Error","MESMER exited with error code %i. Please check the output log for more information." % w.pHandle.returncode,parent=w)
		w.abortButton.config(state=tk.DISABLED)
		w.statusText.set('Error')
		updateLogWindow( w )
		return

def updateLogWindow( w ):
	while(True):
		try:
			line = w.pHandle_Q.get_nowait()
		except Empty: # read until queue is empty
			return

		if( 'INFO: Reading target file' in line):
			w.statusText.set('Reading targets...')
		elif( 'INFO: Found ' in line and 'component files' in line):
			w.statusText.set('Loading components...')
		elif( 'Optimizing parent component ratios' in line):
			w.statusText.set('Optimizing component ratios...')
		elif( 'Optimizing offspring component ratios' in line):
			w.statusText.set('Optimizing component ratios...')
		elif( 'Calculating best fit statistics' in line):
			w.statusText.set('Finding best fit intervals...')

		count = int(w.logWindow.logText.index('end').split('.')[0])
		if( " progress:" in line ): # carriage return
			w.logWindow.logText.delete("%i.0" % (count-2),"%i.0" % (count-1))

		w.logWindow.logText.insert(tk.END,line)
		#w.logWindow.logText.insert(tk.END,line.replace("\r",''))
	return