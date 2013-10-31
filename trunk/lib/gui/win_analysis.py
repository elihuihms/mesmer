import os
import shelve
import Tkinter as tk
import tkFont
import tkFileDialog
import tkMessageBox

import lib.gui.tools_run # to avoid circular import of AnalysisWindow
from lib.gui.tools_analysis	import *
from lib.gui.tools_plot		import *
from lib.gui.tools_plugin	import getGUIPlotPlugins
from lib.gui.win_log		import LogWindow

class AnalysisWindow(tk.Frame):
	def __init__(self, master, path=None, pHandle=None):
		self.master = master
		self.master.title('MESMER Run / Analysis')
		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master)
		self.grid()

		self.loadPrefs()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()

		self.logWindow = None
		self.logWindowMaster = None
		self.pluginOptions = {}

		self.path = path
		self.pHandle = pHandle
		if( path != None and pHandle != None ):
			self.abortButton.config(state=tk.NORMAL)
			lib.gui.tools_run.connectToRun(self,path,pHandle)

	def loadPrefs(self):
		try:
			self.prefs = shelve.open( os.path.join(os.path.dirname(__file__),'preferences'), 'c' )
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file: %s' % (e),parent=self)
			self.master.destroy()

		try:
			self.plot_plugins = getGUIPlotPlugins(self.prefs['mesmer_dir'])
		except Exception as e:
			tkMessageBox.showerror("Error",'Failure loading GUI plot plugins.\n\nReported error:%s' % e,parent=self)
			self.master.destroy()

	def close(self):
		if( self.pHandle and self.pHandle.poll() == None):
			self.abortCurrentRun()
		self.master.destroy()

	def abortCurrentRun(self):
		result = tkMessageBox.askyesno('Cancel Run',"Are you sure you want to cancel a run in progress?")
		if(result):
			self.pHandle.kill()
			self.abortButton.config(state=tk.DISABLED)

	def setWorkFolder(self):
		tmp = tkFileDialog.askdirectory(title='Select Results Directory',mustexist=True,parent=self)
		if(tmp != ''):
			openRunDir(self, tmp)

	def setAttributeTable(self):
		tmp = tkFileDialog.askopenfilename(title='Select PDB attribute table',parent=self)
		if(tmp != ''):
			self.attributeTable.set(tmp)

	def setGenerationSel( self, evt=None ):
		if(len(self.generationsList.curselection())<1):
			return
		self.currentSelection[0] = int(self.generationsList.curselection()[0])

		self.targetsList.delete(0, tk.END)
		for name in self.resultsDB['ensemble_stats'][self.currentSelection[0] ]['target']:
			string = "%s%s%s%s" % (
				name[:14].ljust(14),
				"%.3e".ljust(6) % self.resultsDB['ensemble_stats'][ self.currentSelection[0] ]['target'][name][0],
				"%.3e".ljust(6) % self.resultsDB['ensemble_stats'][ self.currentSelection[0] ]['target'][name][1],
				"%.3e".ljust(6) % self.resultsDB['ensemble_stats'][ self.currentSelection[0] ]['target'][name][2]
				)
			self.targetsList.insert(tk.END, string )

		self.targetsList.selection_set(0)
		self.targetsList.see(0)
		self.setTargetSel()
		self.setWidgetAvailibility()
		return

	def setTargetSel( self, evt=None ):
		if(len(self.targetsList.curselection())<1):
			return

		for (i,name) in enumerate(self.resultsDB['ensemble_stats'][ self.currentSelection[0] ]['target'].keys()):
			if(i == int(self.targetsList.curselection()[0])):
				self.currentSelection[1] = name

		self.restraintsList.delete(0, tk.END)
		for type in self.resultsDB['restraint_stats'][ self.currentSelection[0] ]:
			if(type == 'Total'):
				break
			string = "%s%s%s%s" % (
			type.ljust(14),
			"%.3e".ljust(6) % self.resultsDB['restraint_stats'][ self.currentSelection[0] ][type][ self.currentSelection[1] ][0],
			"%.3e".ljust(6) % self.resultsDB['restraint_stats'][ self.currentSelection[0] ][type][ self.currentSelection[1] ][1],
			"%.3e".ljust(6) % self.resultsDB['restraint_stats'][ self.currentSelection[0] ][type][ self.currentSelection[1] ][2]
			)
			self.restraintsList.insert(tk.END, string )

		self.restraintsList.selection_set(0)
		self.restraintsList.see(0)
		self.setRestraintSel()
		self.setWidgetAvailibility()
		return

	def setRestraintSel( self, evt=None ):
		if(len(self.restraintsList.curselection())<1):
			return

		for (i,type) in enumerate(self.resultsDB['restraint_stats'][ self.currentSelection[0] ].keys()):
			if(i == int(self.restraintsList.curselection()[0])):
				self.currentSelection[2] = type

		path = (os.path.join(self.activeDir.get(), 'restraints_%s_%s_%05i.out' % (self.currentSelection[1],self.currentSelection[2],int(self.currentSelection[0]))))
		if(os.path.exists(path)):
			self.fitPlotButton.config(state=tk.NORMAL)
		else:
			self.fitPlotButton.config(state=tk.DISABLED)
		return

	def setWidgetAvailibility( self ):
		if( self.currentSelection[0] == None):
			self.histogramPlotButton.config(state=tk.DISABLED)
		else:
			self.histogramPlotButton.config(state=tk.NORMAL)

		if( self.currentSelection[0] == None or self.currentSelection[1] == None ):
			self.correlationPlotButton.config(state=tk.DISABLED)
			self.writePDBsButton.config(state=tk.DISABLED)
		else:
			self.correlationPlotButton.config(state=tk.NORMAL)
			self.writePDBsButton.config(state=tk.NORMAL)

		if( self.currentSelection[0] == None or self.currentSelection[1] == None or self.attributeTable.get() == ''):
			self.attributePlotButton.config(state=tk.DISABLED)
			self.attributePlotButton.config(state=tk.DISABLED)
		else:
			self.attributePlotButton.config(state=tk.NORMAL)
			self.attributePlotButton.config(state=tk.NORMAL)

	def createControlVars(self):
		self.activeDir = tk.StringVar()
		self.statusText = tk.StringVar()
		self.statusText.set('Not Loaded')
		self.attributeTable = tk.StringVar()

	def createWidgets(self):
		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		monospaceFont = tkFont.Font(family='Courier',weight='bold')

		self.f_logo = tk.Frame(self.container)
		self.f_logo.grid(column=0,row=0,columnspan=3,sticky=tk.W,pady=(0,8))
		self.LogoImage = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'mesmer_logo.gif'))
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.LEFT)
		self.versionLabel = tk.Label(self.f_logo,text='GUI version 2013.09.18')
		self.versionLabel.pack(side=tk.LEFT,anchor=tk.NE)

		self.activeDirLabel = tk.Label(self.container,text='Work Folder:')
		self.activeDirLabel.grid(in_=self.container,column=0,row=1,sticky=tk.E)
		self.activeDirEntry = tk.Entry(self.container,textvariable=self.activeDir,width=30)
		self.activeDirEntry.grid(in_=self.container,column=1,row=1,sticky=tk.W)
		self.activeDirButton = tk.Button(self.container,text='Set...',command=self.setWorkFolder)
		self.activeDirButton.grid(in_=self.container,column=2,row=1,sticky=tk.W)

		self.statusTextLabel = tk.Label(self.container,text='Run Status:')
		self.statusTextLabel.grid(in_=self.container,column=0,row=2,sticky=tk.E,pady=(0,4))
		self.statusTextEntry = tk.Label(self.container,textvariable=self.statusText)
		self.statusTextEntry.grid(in_=self.container,column=1,row=2,sticky=tk.W,pady=(0,4))
		self.abortButton = tk.Button(self.container,text='Abort',command=self.abortCurrentRun,state=tk.DISABLED)
		self.abortButton.grid(in_=self.container,column=2,row=2,sticky=tk.W,pady=(0,4))

		self.f_generations = tk.LabelFrame(self.container,text='Generations')
		self.f_generations.grid(in_=self.container,column=0,row=3,columnspan=3)
		self.generationsList = tk.Listbox(self.f_generations,width=48,height=6,font=monospaceFont,selectmode=tk.BROWSE,exportselection=False)
		self.generationsList.grid(in_=self.f_generations,sticky=tk.W,padx=(6,0),pady=(2,0),column=0,row=0)
		self.generationsListScroll = tk.Scrollbar(self.f_generations,orient=tk.VERTICAL)
		self.generationsListScroll.grid(in_=self.f_generations,column=2,row=0,sticky=tk.W+tk.N+tk.S,pady=(2,0))
		self.generationsList.config(yscrollcommand=self.generationsListScroll.set)
		self.generationsListScroll.config(command=self.generationsList.yview)
		self.generationsList.bind('<<ListboxSelect>>',self.setGenerationSel)
		self.histogramPlotButton = tk.Button(self.f_generations,text='Ensemble Histogram...',state=tk.DISABLED,command=lambda: plotHistogram(self))
		self.histogramPlotButton.grid(in_=self.f_generations,column=0,row=2,padx=(6,0),pady=(0,4),sticky=tk.W)

		self.f_targets = tk.LabelFrame(self.container,text='Targets')
		self.f_targets.grid(in_=self.container,column=0,row=4,columnspan=3)
		self.targetsList = tk.Listbox(self.f_targets,width=48,height=5,font=monospaceFont,selectmode=tk.BROWSE,exportselection=False)
		self.targetsList.grid(in_=self.f_targets,sticky=tk.W,padx=(6,0),pady=(2,0),column=0,row=0,columnspan=5)
		self.targetsListScroll = tk.Scrollbar(self.f_targets,orient=tk.VERTICAL)
		self.targetsListScroll.grid(in_=self.f_targets,column=6,row=0,sticky=tk.W+tk.N+tk.S,pady=(2,0))
		self.targetsList.config(yscrollcommand=self.targetsListScroll.set)
		self.targetsListScroll.config(command=self.targetsList.yview)
		self.targetsList.bind('<<ListboxSelect>>',self.setTargetSel)

		self.attributePlotButton = tk.Button(self.f_targets,text='Attribute Plot...',state=tk.DISABLED,command=lambda: plotAttributes(self))
		self.attributePlotButton.grid(in_=self.f_targets,column=0,row=1,padx=(6,0),sticky=tk.W)
		self.correlationPlotButton = tk.Button(self.f_targets,text='Correlation Plot...',state=tk.DISABLED,command=lambda: makeCorrelationPlot(self))
		self.correlationPlotButton.grid(in_=self.f_targets,column=1,row=1,columnspan=2)
		self.writePDBsButton = tk.Button(self.f_targets,text='Write PDBs...',state=tk.DISABLED,command=lambda: makePDBs(self))
		self.writePDBsButton.grid(in_=self.f_targets,column=3,row=1,columnspan=2)

		self.attributeTableEntry = tk.Entry(self.f_targets,textvariable=self.attributeTable,width=30)
		self.attributeTableEntry.grid(in_=self.f_targets,padx=(6,0),pady=(0,4),column=0,row=2,columnspan=2,sticky=tk.W)
		self.attributeTableButton = tk.Button(self.f_targets,text='Set...',command=self.setAttributeTable)
		self.attributeTableButton.grid(in_=self.f_targets,pady=(0,4),column=2,row=2,sticky=tk.W,columnspan=3)

		self.f_restraints = tk.LabelFrame(self.container,text='Restraints')
		self.f_restraints.grid(in_=self.container,column=0,row=5,columnspan=3)
		self.restraintsList = tk.Listbox(self.f_restraints,width=48,height=5,font=monospaceFont,selectmode=tk.BROWSE,exportselection=False)
		self.restraintsList.grid(in_=self.f_restraints,sticky=tk.W,padx=(6,0),pady=(2,0),column=0,row=0)
		self.restraintsListScroll = tk.Scrollbar(self.f_restraints,orient=tk.VERTICAL)
		self.restraintsListScroll.grid(in_=self.f_restraints,column=1,row=0,sticky=tk.W+tk.N+tk.S,pady=(2,0))
		self.restraintsList.config(yscrollcommand=self.restraintsListScroll.set)
		self.restraintsListScroll.config(command=self.restraintsList.yview)
		self.restraintsList.bind('<<ListboxSelect>>',self.setRestraintSel)

		self.fitPlotButton = tk.Button(self.f_restraints,text='Fit Plot...',width=12,command=lambda: plotRestraint(self))
		self.fitPlotButton.grid(in_=self.f_restraints,column=0,row=1,padx=(6,0),pady=(0,4),sticky=tk.W)

		self.f_footer = tk.Frame(self.container)
		self.f_footer.grid(in_=self.container,column=0,row=6,columnspan=3)

		self.openLogButton = tk.Button(self.f_footer,text='Open Log',width=8,state=tk.DISABLED,command=lambda: openLogWindow(self,self.path))
		self.openLogButton.grid(in_=self.f_footer,column=0,row=0,pady=(4,0))
		self.cancelButton = tk.Button(self.f_footer,text='Cancel',width=8,command=self.close)
		self.cancelButton.grid(in_=self.f_footer,column=1,row=0,pady=(4,0))

	def createToolTips(self):
		pass
