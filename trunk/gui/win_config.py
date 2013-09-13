import os
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import shelve

from gui.tools_TkTooltip	import ToolTip
from gui.tools_general		import getWhichPath

class ConfigWindow(tk.LabelFrame):
	def __init__(self, master, mainWindow):
		self.master = master
		self.mainWindow = mainWindow
		self.master.resizable(width=False, height=False)
		self.master.title('Configuration Panel')

		tk.LabelFrame.__init__(self,master,width=420,height=150,borderwidth=0)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()

	def loadPrefs(self):
		try:
			self.prefs = shelve.open( os.path.join(os.getcwd(),'gui','preferences') )
		except:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file. Perhaps MESMER is running in a read-only directory?',parent=self)
			self.master.destroy()

	def setEXEPath(self):
		tmp = tkFileDialog.askopenfilename(title='Select MESMER command-line program:',parent=self)
		if(tmp != ''):
			self.mesmerEXEPath.set(os.path.abspath(tmp))

	def setUtilPath(self):
		tmp = tkFileDialog.askdirectory(title='Select MESMER utilities directory',mustexist=True,parent=self)
		if(tmp != ''):
			self.mesmerUtilPath.set(os.path.abspath(tmp))

	def checkPaths(self):
		ok = True
		path0 = os.path.dirname(self.mesmerEXEPath.get())
		path1 = self.mesmerEXEPath.get()
		path2 = os.path.join(self.mesmerUtilPath.get(),'make_components')

		if(not os.path.isdir(path0)):
			tkMessageBox.showwarning("Warning","The folder containing the MESMER executable was not found.",parent=self)
			ok = False
		if(not os.path.isfile(path1)):
			tkMessageBox.showwarning("Warning","The MESMER executable was not found.",parent=self)
			ok = False
		elif(not os.access(path1, os.X_OK)):
			tkMessageBox.showwarning("Warning","The MESMER install is damaged.",parent=self)
			ok = False
		if(not os.access(path2, os.X_OK)):
			tkMessageBox.showwarning("Warning","The MESMER utilities are missing.",parent=self)
			ok = False
		if(ok):
			tkMessageBox.showinfo("Setup Check","Configuration is OK.",parent=self)

			self.prefs['mesmer_dir'] = os.path.dirname(self.mesmerEXEPath.get())
			self.prefs['mesmer_exe_path'] = self.mesmerEXEPath.get()
			self.prefs['mesmer_util_path'] = self.mesmerUtilPath.get()
			self.prefs.close()
			self.mainWindow.Ready = True
			self.mainWindow.updateWidgets()
			self.master.destroy()

	def closeWindow(self):
		self.master.destroy()

	def createControlVars(self):
		self.mesmerEXEPath 		= tk.StringVar()
		self.mesmerUtilPath 	= tk.StringVar()

		if(self.prefs.has_key('mesmer_exe_path')):
			self.mesmerEXEPath.set( self.prefs['mesmer_exe_path'] )
		else:
			self.mesmerEXEPath.set(	os.path.join(os.getcwd(),'mesmer') )

		if(self.prefs.has_key('mesmer_util_path')):
			self.mesmerUtilPath.set( self.prefs['mesmer_util_path'] )
		else:
			self.mesmerUtilPath.set(os.path.join(os.getcwd(),'utilities') )

	def createToolTips(self):
		#self.createTargetTT 	= ToolTip(self.createTargetButton,		follow_mouse=0,text='Create a target file from experimental data')
		pass

	def createWidgets(self):
		self.container = tk.Frame(self,borderwidth=0)
		self.container.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.mesmerEXEPathLabel = tk.Label(self.container, text='Path to MESMER command-line program:')
		self.mesmerEXEPathLabel.grid(in_=self.container,column=0,row=0,columnspan=2,sticky=tk.W)
		self.mesmerEXEPathEntry = tk.Entry(self.container,width=40,textvariable=self.mesmerEXEPath)
		self.mesmerEXEPathEntry.grid(in_=self.container,column=0,row=1,sticky=tk.E)
		self.mesmerEXEPathButton = tk.Button(self.container, text='Set...',command=self.setEXEPath)
		self.mesmerEXEPathButton.grid(in_=self.container,column=1,row=1,sticky=tk.W)

		self.mesmerUtilPathLabel = tk.Label(self.container, text='Path to MESMER utilities folder:')
		self.mesmerUtilPathLabel.grid(in_=self.container,column=0,row=2,columnspan=2,sticky=tk.W)
		self.mesmerUtilPathEntry = tk.Entry(self.container,width=40,textvariable=self.mesmerUtilPath)
		self.mesmerUtilPathEntry.grid(in_=self.container,column=0,row=3,sticky=tk.E)
		self.mesmerUtilPathButton = tk.Button(self.container, text='Set...',command=self.setUtilPath)
		self.mesmerUtilPathButton.grid(in_=self.container,column=1,row=3,sticky=tk.W)

		self.mesmerCheckButton = tk.Button(self.container, text='Cancel',command=self.closeWindow)
		self.mesmerCheckButton.grid(in_=self.container,column=0,row=4,sticky=tk.E,pady=10)
		self.mesmerDoneButton = tk.Button(self.container, text='Check...',default=tk.ACTIVE,command=self.checkPaths)
		self.mesmerDoneButton.grid(in_=self.container,column=1,row=4,sticky=tk.W,pady=10)
