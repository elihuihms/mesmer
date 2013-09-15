import os
import Tkinter as tk
import tkMessageBox

from win_analysis	import AnalysisWindow

def startRun( mainWindow, mesmerPath, args ):
	
	if(not os.path.isfile(mesmerPath) or not os.access(mesmerPath, os.X_OK) ):
		tkMessageBox.showerror("Error","Error accessing MESMER executable at \"%s\"" % mesmerPath)
		return False
			
	mainWindow.masters.append( tk.Toplevel(mainWindow.master) )
	mainWindow.windows.append( AnalysisWindow(mainWindow.masters[-1],os.path.join(args.dir,args.name)) )
			
	return True