import os
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import shelve
import multiprocessing

from mesmer.lib.setup_functions	import open_user_prefs,set_default_prefs

from tools_TkTooltip	import ToolTip
from tools_general		import tryProgramCall

class ConfigWindow(tk.LabelFrame):
	def __init__(self, master, mainWindow):
		self.master = master
		self.mainWindow = mainWindow
		self.master.title('Configuration Panel')
		
		self.master.resizable(width=False, height=False)		
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.LabelFrame.__init__(self,master,width=420,height=190,borderwidth=0)
		self.pack(expand=True,fill='both',padx=4,pady=4)
		self.pack_propagate(True)

		self.loadPrefs()
		self.createWidgets()
		self.setVars()

	def loadPrefs(self):
		try:
			self.prefs = open_user_prefs( mode='c' )
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read or create MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()

	def savePrefs(self):
#		self.prefs['mesmer_base_dir']	= self.mesmerPath.get()
		self.prefs['mesmer_scratch']	= self.scratchPath.get()
		self.prefs['cpu_count']			= self.numCores.get()

		# append mesmer run arguments
		tmp = self.prefs['run_arguments']

		if(self.prefs['mesmer_scratch'] != ''):
			tmp['scratch'] = self.prefs['mesmer_scratch']
		tmp['threads'] = self.prefs['cpu_count']
		self.prefs['run_arguments'] = tmp

		self.prefs.close()
		self.loadPrefs() #reload, due to to broken db implementation in some OSes
		
	def resetPrefs(self):
		self.prefs = open_user_prefs( mode='c' )
		set_default_prefs( self.prefs )
		self.savePrefs()
		self.setVars()

	def setVars(self):
#		if(self.prefs.has_key('mesmer_base_dir')):
#			self.mesmerPath.set( self.prefs['mesmer_base_dir'] )
#		else:
#			self.mesmerPath.set( os.getcwd() )

		if(self.prefs.has_key('mesmer_scratch')):
			self.scratchPath.set( self.prefs['mesmer_scratch'] )
		else:
			self.scratchPath.set( '' )

		if(self.prefs.has_key('cpu_count') ):
			self.numCores.set( self.prefs['cpu_count'] )
		else:
			self.numCores.set( multiprocessing.cpu_count() )

#	def setMESMERPath(self):
#		tmp = tkFileDialog.askdirectory(title='Select directory containing MESMER executables, or cancel to leave as default:',mustexist=True,parent=self)
#		self.mesmerPath.set(tmp)

	def setScratchPath(self):
		tmp = tkFileDialog.askdirectory(title='Select directory to use as scratch space, or cancel to use default.',mustexist=True,parent=self)
		self.scratchPath.set(tmp)

	def checkPaths(self):
		ok = True
#		if(self.mesmerPath.get() == ''):
#			if(not tryProgramCall('mesmer')):
#				tkMessageBox.showwarning("Warning","The MESMER executables are not available on the system path.\nTry resetting the MESMER preferences, or setting the MESMER installation path manually.",parent=self)
#				ok = False
#		elif(not os.access(os.path.join(self.mesmerPath.get(),'mesmer.py'), os.R_OK)):
#			tkMessageBox.showwarning("Warning","MESMER executables are not installed in this directory.",parent=self)
#			ok = False
		
		if(self.scratchPath.get() != '' and not os.access(self.scratchPath.get(), os.W_OK)):
			tkMessageBox.showwarning("Warning","The MESMER scratch path is not writable.",parent=self)
			ok = False			
		
		if(ok):
			self.savePrefs()
			self.mainWindow.Ready = True
			self.mainWindow.updateWidgets()
			self.master.destroy()			

	def close(self):
		self.prefs.close()
		self.master.destroy()

	def createWidgets(self):
		self.container = tk.Frame(self,borderwidth=0)
		self.container.pack()
		
#		self.mesmerPath = tk.StringVar()
#		self.mesmerPathLabel = tk.Label(self.container, text='Explicit path to MESMER installation:')
#		self.mesmerPathLabel.grid(column=0,row=0,columnspan=3,sticky=tk.W)
#		self.mesmerPathEntry = tk.Entry(self.container,width=40,textvariable=self.mesmerPath)
#		self.mesmerPathEntry.grid(column=0,columnspan=2,row=1,sticky=tk.E)
#		self.mesmerPathButton = tk.Button(self.container, text='Set...',command=self.setMESMERPath)
#		self.mesmerPathButton.grid(column=2,columnspan=2,row=1,sticky=tk.W)

		self.scratchPath = tk.StringVar()
		self.mesmerScratchLabel = tk.Label(self.container, text='Directory to use as scratch space:')
		self.mesmerScratchLabel.grid(column=0,row=2,columnspan=3,sticky=tk.W)
		self.mesmerScratchEntry = tk.Entry(self.container,width=40,textvariable=self.scratchPath)
		self.mesmerScratchEntry.grid(column=0,columnspan=2,row=3,sticky=tk.E)
		self.mesmerScratchButton = tk.Button(self.container, text='Set...',command=self.setScratchPath)
		self.mesmerScratchButton.grid(column=2,row=3,sticky=tk.W)

		self.numCores = tk.IntVar()
		self.numCoresLabel = tk.Label(self.container, text='Number of cores to use for multithreading:')
		self.numCoresLabel.grid(column=0,row=4,sticky=tk.W,pady=10)
		self.numCoresEntry = tk.Spinbox(self.container,width=10,textvariable=self.numCores,from_=1,to=24)
		self.numCoresEntry.grid(column=1,columnspan=2,row=4,sticky=tk.E,pady=10)
		
		self.resetPrefsButton = tk.Button(self.container, text='Reset Preferences',command=self.resetPrefs)
		self.resetPrefsButton.grid(column=0,row=5,sticky=tk.W,pady=6)
		self.mesmerCheckButton = tk.Button(self.container, text='Close',command=self.close)
		self.mesmerCheckButton.grid(column=1,row=5,sticky=tk.E,pady=6)
		self.mesmerDoneButton = tk.Button(self.container, text='Save',default=tk.ACTIVE,command=self.checkPaths)
		self.mesmerDoneButton.grid(column=2,row=5,sticky=tk.W,pady=6)
