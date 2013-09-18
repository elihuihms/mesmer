import os
import time
import shutil
import Tkinter as tk
import tkMessageBox

from subprocess			import Popen,PIPE,STDOUT

from gui.tools_setup	import makeMESMERArgsFromWindow,makeStringFromArgs
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