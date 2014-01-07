import os
import sys
import shelve
import Tkinter as tk
import tkMessageBox

from lib.gui.tools_TkTooltip	import ToolTip
from lib.gui.tools_plugin		import getTargetPluginOptions
from lib.gui.win_target			import TargetWindow
from lib.gui.win_components		import ComponentsWindow
from lib.gui.win_setup			import SetupWindow
from lib.gui.win_config			import ConfigWindow
from lib.gui.win_analysis		import AnalysisWindow
from lib.gui.win_about			import AboutWindow,programInfo

class MainWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.geometry('500x300+200+200')
		self.master.resizable(width=False, height=False)
		self.master.title('MESMER')

		tk.Frame.__init__(self,master,width=500,height=300)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()

		self.createMenus()
		self.createWidgets()
		self.createToolTips()
		self.updateWidgets()

		self.masters	= []
		self.windows	= []
		self.setupMaster	= None
		self.configMaster	= None
		self.aboutMaster	= None

	def loadPrefs(self):
		self.Ready = True

		try:
			self.prefs = shelve.open( os.path.join(os.path.dirname(__file__),'preferences'), 'c' )
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file: %s' % (e),parent=self)
			self.close(1)

		if( self.prefs.has_key('mesmer_dir') ):
			path0 = self.prefs['mesmer_dir']
			path1 = self.prefs['mesmer_exe_path']
			path2 = self.prefs['mesmer_util_path']
		else:
			path0 = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
			path1 = os.path.join(path0,'mesmer.py')
			path2 = os.path.join(path0,'utilities')

		if(not os.path.isdir(path0)):
			self.Ready = False
		if(not os.path.isfile(path1)):
			self.Ready = False
		elif(not os.access(path1, os.X_OK)):
			self.Ready = False
		if(not os.access(os.path.join(path2,'make_components.py'), os.X_OK)):
			self.Ready = False

		self.prefs['mesmer_dir'] = path0
		self.prefs['mesmer_exe_path'] = path1
		self.prefs['mesmer_util_path'] = os.path.join(path0,'utilities')
		self.prefs.sync()

		# preload plugins
		try:
			(self.plugin_types,self.plugin_options) = getTargetPluginOptions(self.prefs['mesmer_dir'])
		except Exception as e:
			tkMessageBox.showerror("Error",'Failure loading MESMER plugins.\n\nReported error:%s' % e,parent=self)
			self.close(1)

		self.prefs.close()

	def createMenus(self):
		self.topMenu = tk.Menu(self.master)
		self.master.config(menu=self.topMenu)

		self.fileMenu = tk.Menu(self.topMenu)
		self.fileMenu.add_command(label='About MESMER...', command=self.setupAbout)
		self.fileMenu.add_command(label='Quit', accelerator="Ctrl+Q", command=self.close)

		self.actionMenu = tk.Menu(self.topMenu)
		self.actionMenu.add_command(label='Make Target', accelerator="Ctrl+T", command=self.makeTarget)
		self.actionMenu.add_command(label='Make Components', accelerator="Ctrl+K", command=self.makeComponents)
		self.actionMenu.add_command(label='Setup Run', accelerator="Ctrl+R", command=self.setupMESMER)
		self.actionMenu.add_command(label='Analyze Run', accelerator="Ctrl+Y", command=self.openAnalysis)

		self.topMenu.add_cascade(label="File", menu=self.fileMenu)
		self.topMenu.add_cascade(label="Actions", menu=self.actionMenu)

		self.master.bind_all("<Control-q>", lambda a: sys.exit(0) )
		self.master.bind_all("<Control-t>", lambda a: self.makeTarget() )
		self.master.bind_all("<Control-k>", lambda a: self.makeComponents() )
		self.master.bind_all("<Control-r>", lambda a: self.setupMESMER() )
		self.master.bind_all("<Control-y>", lambda a: self.openAnalysis() )

	def close(self, returncode=0):
		self.master.destroy()
		sys.exit(returncode)

	def makeTarget(self):
		self.masters.append( tk.Toplevel(self.master) )
		self.windows.append( TargetWindow(self.masters[-1]) )

	def makeTarget(self):
		self.masters.append( tk.Toplevel(self.master) )
		self.windows.append( TargetWindow(self.masters[-1]) )

	def makeComponents(self):
		self.masters.append( tk.Toplevel(self.master) )
		self.windows.append( ComponentsWindow(self.masters[-1]) )

	def openAnalysis(self):
		self.masters.append( tk.Toplevel(self.master) )
		self.windows.append( AnalysisWindow(self.masters[-1]) )

	def setupMESMER(self):
		if(self.setupMaster == None or not self.setupMaster.winfo_exists()):
			self.setupMaster = tk.Toplevel(self.master)
			self.setupWindow = SetupWindow(self.setupMaster,self)

	def setConfig(self):
		if(self.configMaster == None or not self.configMaster.winfo_exists()):
			self.configMaster = tk.Toplevel(self.master)
			self.configWindow = ConfigWindow(self.configMaster,self)

	def setupAbout(self):
		if(self.aboutMaster == None or not self.aboutMaster.winfo_exists()):
			self.aboutMaster = tk.Toplevel(self.master)
			self.aboutMaster = AboutWindow(self.aboutMaster)

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
		self.f_buttons = tk.Frame(self)
		self.f_buttons.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.f_logo = tk.Frame(self.f_buttons)
		self.f_logo.grid(column=0,row=0,pady=20)
		self.LogoImage = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'mesmer_logo.gif'))
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.TOP)
		self.versionLabel = tk.Label(self.f_logo,text='GUI version %s' % programInfo['version'])
		self.versionLabel.pack(side=tk.TOP,anchor=tk.NE)

		self.createTargetButton = tk.Button(self.f_buttons, text='Create Target', command=self.makeTarget,width=20,height=1)
		self.createTargetButton.grid(in_=self.f_buttons,column=0,row=1,sticky=tk.S)

		self.createComponentsButton = tk.Button(self.f_buttons, text='Create Components', command=self.makeComponents,width=20,height=1)
		self.createComponentsButton.grid(in_=self.f_buttons,column=0,row=2,sticky=tk.S)

		self.runMESMERButton = tk.Button(self.f_buttons, text='Run MESMER', command=self.setupMESMER,width=20,height=1)
		self.runMESMERButton.grid(in_=self.f_buttons,column=0,row=3,sticky=tk.S)

		self.analyzeDataButton = tk.Button(self.f_buttons, text='Analyze Run Data', command=self.openAnalysis,width=20,height=1)
		self.analyzeDataButton.grid(in_=self.f_buttons,column=0,row=4,sticky=tk.S)

		self.configureButton = tk.Button(self.f_buttons, text='Configure',width=20,height=1,command=self.setConfig)
		self.configureButton.grid(in_=self.f_buttons,column=0,row=5,sticky=tk.S,pady=10)
