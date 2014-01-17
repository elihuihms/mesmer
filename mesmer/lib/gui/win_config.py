import os
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import shelve
import multiprocessing

from tools_TkTooltip	import ToolTip
from tools_general		import openUserPrefs,tryProgramCall

class ConfigWindow(tk.LabelFrame):
	def __init__(self, master, mainWindow):
		self.master = master
		self.mainWindow = mainWindow
		self.master.resizable(width=False, height=False)
		self.master.title('Configuration Panel')
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.LabelFrame.__init__(self,master,width=420,height=190,borderwidth=0)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()

	def loadPrefs(self):
		try:
			self.prefs = openUserPrefs( mode='c' )
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read or create MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()

	def savePrefs(self):
		self.prefs['mesmer_base_dir']	= self.mesmerPath.get()
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

	def setMESMERPath(self):
		tmp = tkFileDialog.askdirectory(title='Select directory containing MESMER executables, or cancel to leave as default:',mustexist=True,parent=self)
		if(tmp != ''):
			self.mesmerPath.set(tmp)

	def setScratchPath(self):
		tmp = tkFileDialog.askdirectory(title='Select directory to use as scratch space. Cancel to use default.',mustexist=True,parent=self)
		self.scratchPath.set(tmp)

	def checkPaths(self):
		ok = True
		if(self.mesmerPath.get() == ''):
			if(not tryProgramCall('mesmer')):
				tkMessageBox.showwarning("Warning","The MESMER executables are not available.",parent=self)
				ok = False
		elif(not os.access(os.path.join(self.mesmerPath.get(),'mesmer.py'), os.R_OK)):
			tkMessageBox.showwarning("Warning","MESMER executables are not installed in this directory.",parent=self)
			ok = False
		
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

	def createControlVars(self):
		self.mesmerPath 		= tk.StringVar()
		self.scratchPath 		= tk.StringVar()
		self.numCores			= tk.IntVar()

		if(self.prefs.has_key('mesmer_base_dir')):
			self.mesmerPath.set( self.prefs['mesmer_base_dir'] )
		else:
			self.mesmerPath.set( os.getcwd() )

		if(self.prefs.has_key('mesmer_scratch')):
			self.scratchPath.set( self.prefs['mesmer_scratch'] )
		else:
			self.scratchPath.set( '' )

		if(self.prefs.has_key('cpu_count') ):
			self.numCores.set( self.prefs['cpu_count'] )
		else:
			self.numCores.set( multiprocessing.cpu_count() )

	def createToolTips(self):
		#self.createTargetTT 	= ToolTip(self.createTargetButton,		follow_mouse=0,text='Create a target file from experimental data')
		pass

	def createWidgets(self):
		self.container = tk.Frame(self,borderwidth=0)
		self.container.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.mesmerPathLabel = tk.Label(self.container, text='Explicit path to MESMER installation:')
		self.mesmerPathLabel.grid(in_=self.container,column=0,row=0,columnspan=2,sticky=tk.W)
		self.mesmerPathEntry = tk.Entry(self.container,width=40,textvariable=self.mesmerPath)
		self.mesmerPathEntry.grid(in_=self.container,column=0,row=1,sticky=tk.E)
		self.mesmerPathButton = tk.Button(self.container, text='Set...',command=self.setMESMERPath)
		self.mesmerPathButton.grid(in_=self.container,column=1,row=1,sticky=tk.W)

		self.mesmerScratchLabel = tk.Label(self.container, text='Directory to use as scratch space:')
		self.mesmerScratchLabel.grid(in_=self.container,column=0,row=2,columnspan=2,sticky=tk.W)
		self.mesmerScratchEntry = tk.Entry(self.container,width=40,textvariable=self.scratchPath)
		self.mesmerScratchEntry.grid(in_=self.container,column=0,row=3,sticky=tk.E)
		self.mesmerScratchButton = tk.Button(self.container, text='Set...',command=self.setScratchPath)
		self.mesmerScratchButton.grid(in_=self.container,column=1,row=3,sticky=tk.W)

		self.numCoresLabel = tk.Label(self.container, text='Number of cores to use for multithreading:')
		self.numCoresLabel.grid(in_=self.container,column=0,row=4,columnspan=2,sticky=tk.W)
		self.numCoresEntry = tk.Spinbox(self.container,width=10,textvariable=self.numCores,from_=1,to=24)
		self.numCoresEntry.grid(in_=self.container,column=0,row=5,sticky=tk.W)

		self.mesmerCheckButton = tk.Button(self.container, text='Cancel',command=self.close)
		self.mesmerCheckButton.grid(in_=self.container,column=0,row=6,sticky=tk.E)
		self.mesmerDoneButton = tk.Button(self.container, text='Save',default=tk.ACTIVE,command=self.checkPaths)
		self.mesmerDoneButton.grid(in_=self.container,column=1,row=6,sticky=tk.W)
