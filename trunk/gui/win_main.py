#!/usr/bin/env python

import os
import shelve
import Tkinter as tk
import tkMessageBox

from lib.setup			import parse_param_arguments
from gui.tools_TkTooltip	import ToolTip
from gui.win_target		import TargetWindow
from gui.win_components	import ComponentsWindow
from gui.win_run		import RunWindow
from gui.win_config		import ConfigWindow

class MainWindow(tk.LabelFrame):
	def __init__(self, master=None):
		self.master = master
		self.master.resizable(width=False, height=False)
		self.master.title('MESMER')

		self.loadPrefs()

		tk.LabelFrame.__init__(self,master,width=500,height=300)
		self.grid()
		self.grid_propagate(0)

		self.createWidgets()
		self.createToolTips()
		self.updateWidgets()

	def loadPrefs(self):
		self.Ready = True

		try:
			self.prefs = shelve.open( os.path.join(os.getcwd(),'gui','preferences') )
		except:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file. Perhaps MESMER is running in a read-only directory?',parent=self)
			self.master.destroy()

		if(not self.prefs.has_key('mesmer_exe_path')):
			self.Ready = False
		if(not self.prefs.has_key('mesmer_util_path')):
			self.Ready = False

	def makeTarget(self):
		self.newWindow = tk.Toplevel(self.master)
		self.makeTargetWindow = TargetWindow(self.newWindow)

	def makeComponents(self):
		self.newWindow = tk.Toplevel(self.master)
		self.makeComponentsWindow = ComponentsWindow(self.newWindow)

	def runMESMER(self):
		self.newWindow = tk.Toplevel(self.master)
		self.runMESMERWindow = RunWindow(self.newWindow)

	def setConfig(self):
		self.newWindow = tk.Toplevel(self.master)
		self.loadConfigWindow = ConfigWindow(self.newWindow)

	def createToolTips(self):
		self.createTargetTT 	= ToolTip(self.createTargetButton,		follow_mouse=0,text='Create a target file from experimental data')
		self.createComponentsTT = ToolTip(self.createComponentsButton,	follow_mouse=0,text='Create component files from a library of PDBs and calculated data')
		self.runMESMERTT	 	= ToolTip(self.runMESMERButton,			follow_mouse=0,text='Start a MESMER run')
		self.analyzeDataTT	 	= ToolTip(self.analyzeDataButton,		follow_mouse=0,text='Analyze results from a run')
		self.configureTT		= ToolTip(self.configureButton,			follow_mouse=0,text='Configure MESMER to run on your system')

	def updateWidgets(self):
		if(self.Ready):
			state = tk.NORMAL
			self.configureButton.config(default=tk.NORMAL)
		else:
			state = tk.DISABLED
			self.configureButton.config(default=tk.ACTIVE)

		self.createTargetButton.config(state=state)
		self.createComponentsButton.config(state=state)
		self.runMESMERButton.config(state=state)
		self.analyzeDataButton.config(state=state)

	def createWidgets(self):
		self.f_buttons = tk.Frame(self,borderwidth=0)
		self.f_buttons.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.f_logo = tk.Frame(self.f_buttons)
		self.f_logo.grid(column=0,row=0,pady=20)
		self.LogoImage = tk.PhotoImage(file='gui/mesmer_logo.gif')
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.TOP)
		self.versionLabel = tk.Label(self.f_logo,text='GUI version 2013.08.26')
		self.versionLabel.pack(side=tk.TOP,anchor=tk.NE)

		self.createTargetButton = tk.Button(self.f_buttons, text='Create Target', command=self.makeTarget,width=20,height=1)
		self.createTargetButton.grid(in_=self.f_buttons,column=0,row=1,sticky=tk.S)

		self.createComponentsButton = tk.Button(self.f_buttons, text='Create Components', command=self.makeComponents,width=20,height=1)
		self.createComponentsButton.grid(in_=self.f_buttons,column=0,row=2,sticky=tk.S)

		self.runMESMERButton = tk.Button(self.f_buttons, text='Run MESMER', command=self.runMESMER,width=20,height=1)
		self.runMESMERButton.grid(in_=self.f_buttons,column=0,row=3,sticky=tk.S)

		self.analyzeDataButton = tk.Button(self.f_buttons, text='Analyze Run Data', command=self.makeTarget,width=20,height=1)
		self.analyzeDataButton.grid(in_=self.f_buttons,column=0,row=4,sticky=tk.S)

		self.configureButton = tk.Button(self.f_buttons, text='Configure',width=20,height=1,command=self.setConfig)
		self.configureButton.grid(in_=self.f_buttons,column=0,row=5,sticky=tk.S,pady=10)
