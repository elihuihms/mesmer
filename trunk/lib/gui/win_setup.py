import os.path
import copy
import shelve
import Tkinter as tk
import tkFileDialog
import tkMessageBox

from lib.setup_functions	import parse_arguments
from lib.gui.tools_TkTooltip	import ToolTip
from lib.gui.tools_setup		import *
from lib.gui.tools_run			import startRun
from lib.gui.win_about			import programInfo

class SetupWindow(tk.Frame):
	def __init__(self, master, parent):
		self.master = master
		self.master.title('Configure MESMER Run')
		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)
		self.master.bind("<Return>", self.setupAndStartRun)
		self.parent = parent

		tk.Frame.__init__(self,master)
		self.grid(pady=(2,6),padx=6)

		self.loadPrefs()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()

		self.basedir = os.path.expanduser('~')

		# initialize to defaults
		args = parse_arguments('')
		args.dir = self.basedir
		setControlVarsFromMESMERArgs(self, args)

		self.setCheckboxStates()
		self.setButtonStates()

	def loadPrefs(self):
		try:
			self.prefs = shelve.open( os.path.join(os.path.dirname(__file__),'preferences'), 'c' )
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file: %s' % (e),parent=self)
			self.master.destroy()

	def close(self):
		self.prefs.close()
		self.master.destroy()

	def setupAndStartRun(self, evt=None):
		if( startRun( self, self.prefs['mesmer_exe_path'] ) ):
			self.close()

	def setResultsPath(self):
		tmp = tkFileDialog.askdirectory(title='Select Results Directory',mustexist=True,parent=self)
		if(tmp != ''):
			self.saveResults.set(tmp)
			self.basedir = tmp

	def addTargetFile(self):
		tmp = tkFileDialog.askopenfilename(title='Select MESMER Target File(s):',multiple=True,parent=self)
		if(tmp != ''):
			for f in tmp:
				self.targetFilesList.insert(tk.END, os.path.relpath(f,self.basedir))
		self.setButtonStates()

	def delTargetFile(self):
		tmp = map(int, self.targetFilesList.curselection())[0]
		self.targetFilesList.delete(tmp,0)
		self.setButtonStates()

	def addComponentDir(self):
		tmp = tkFileDialog.askdirectory(title='Select Directory containing MESMER components:',mustexist=True,parent=self)
		if(tmp != ''):
			self.componentFilesList.insert(tk.END,  os.path.relpath(tmp,self.basedir))
		self.setButtonStates()

	def delComponentDir(self):
		tmp = map(int, self.componentFilesList.curselection())[0]
		self.componentFilesList.delete(tmp,0)
		self.setButtonStates()

	def setButtonStates(self):
		ok=True

		if(len(self.runTitle.get())==0):
			ok=False

		if(len(list(self.targetFilesList.get(0,tk.END)))<1):
			ok=False
			self.removeTargetButton.config(state=tk.DISABLED)
		else:
			self.removeTargetButton.config(state=tk.NORMAL)
		if(len(list(list(self.componentFilesList.get(0,tk.END))))<1):
			ok=False
			self.removeComponentButton.config(state=tk.DISABLED)
		else:
			self.removeComponentButton.config(state=tk.NORMAL)

		if(ok):
			self.startButton.config(state=tk.NORMAL)
		else:
			self.startButton.config(state=tk.DISABLED)

	def setListStates(self, evt):
		w = evt.widget

		if(w == self.targetFilesList):
			tmp = map(int, self.targetFilesList.curselection())
			if(len(tmp) == 0):
				self.removeTargetButton.config(state=tk.DISABLED)
			else:
				self.removeTargetButton.config(state=tk.NORMAL)

		elif(w == self.componentFilesList):
			tmp = map(int, self.componentFilesList.curselection())
			if(len(tmp) == 0):
				self.removeComponentButton.config(state=tk.DISABLED)
			else:
				self.removeComponentButton.config(state=tk.NORMAL)

		self.setButtonStates()

	def setCheckboxStates(self):
		if(self.minFitnessCheck.get() == 0):
			self.minFitnessEntry.config(state=tk.DISABLED)
		else:
			self.minFitnessEntry.config(state=tk.NORMAL)

		if(self.minRSDCheck.get() == 0):
			self.minRSDEntry.config(state=tk.DISABLED)
		else:
			self.minRSDEntry.config(state=tk.NORMAL)

		if(self.maxGenerationsCheck.get() == 0):
			self.maxGenerationsEntry.config(state=tk.DISABLED)
		else:
			self.maxGenerationsEntry.config(state=tk.NORMAL)

		if(self.componentStatsCheck.get() == 0):
			self.componentStatsEntry.config(state=tk.DISABLED)
		else:
			self.componentStatsEntry.config(state=tk.NORMAL)

		if(self.componentCorrCheck.get() == 0):
			self.componentCorrsEntry.config(state=tk.DISABLED)
		else:
			self.componentCorrsEntry.config(state=tk.NORMAL)

	def createControlVars(self):
		self.runTitle 			= tk.StringVar()
		self.saveResults 		= tk.StringVar()
		self.targetFiles		= tk.StringVar() #NOTE: not used - bug in .get() returns as string, not list
		self.componentFiles		= tk.StringVar() #NOTE: see above, must call self.componentFilesList(box).get() instead
		self.ensembleSize		= tk.IntVar()
		self.numEnsembles		= tk.IntVar()
		self.gCrossFreq			= tk.DoubleVar()
		self.gMutateFreq		= tk.DoubleVar()
		self.gSourceRatio		= tk.DoubleVar()
		self.minFitness			= tk.DoubleVar()
		self.minFitnessCheck	= tk.IntVar()
		self.minRSD				= tk.DoubleVar()
		self.minRSDCheck		= tk.IntVar()
		self.maxGenerations		= tk.IntVar()
		self.maxGenerationsCheck= tk.IntVar()
		self.bestFitCheck		= tk.IntVar()
		self.componentStats		= tk.DoubleVar()
		self.componentStatsCheck= tk.IntVar()
		self.componentStatsCheck.set(1) #always on in MESMER >0.3
		self.componentCorr		= tk.DoubleVar()
		self.componentCorrCheck= tk.IntVar()
		self.componentCorrCheck.set(1) #always on in MESMER >0.3
		self.pluginExtrasCheck	= tk.IntVar()
		self.pluginExtrasCheck.set(1) #enabled by default
		self.optimizationStateCheck = tk.IntVar()
		self.optMethod			= tk.IntVar()
		self.optMethodOptions = ('None','Blind Random','Local Random','Truncated Newtonian','L-BFGS-B','Powell','Simplex')
		self.optMethodOption	= tk.StringVar()
		self.optTolerance		= tk.DoubleVar()
		self.optIterations		= tk.IntVar()

	def createToolTips(self):
		self.runTitleTT 		= ToolTip(self.runTitleEntry,		follow_mouse=0,text='Set the title to be used for the run.')
		self.saveResultsTT 		= ToolTip(self.saveResultsEntry,	follow_mouse=0,text='Set the directory where the results will be saved')
		self.targetFilesTT 		= ToolTip(self.targetFilesList,		follow_mouse=1,text='Specify the target files to be used in the run.')
		self.componentFilesTT 	= ToolTip(self.componentFilesList,	follow_mouse=1,text='Specify the components or directories containing components to be used for the run')

	def createWidgets(self):
		self.f_setup = tk.LabelFrame(self, borderwidth=2, width=400, height=280, relief='groove', text='File Setup')
		self.f_setup.grid(column=0,row=0,columnspan=2,rowspan=2,sticky=tk.NW)
		self.f_setup.grid_propagate(0)

		self.f_logo = tk.Frame(self.f_setup, width=390, height=31 )
		self.f_logo.grid(column=0,row=0,columnspan=5)
		self.LogoImage = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'mesmer_logo.gif'))
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.LEFT)
		self.versionLabel = tk.Label(self.f_logo,text='GUI version %s' % programInfo['version'])
		self.versionLabel.pack(side=tk.LEFT,anchor=tk.NE)

		self.runTitleLabel = tk.Label(self.f_setup,text='Run Title:')
		self.runTitleLabel.grid(in_=self.f_setup,column=0,row=1,sticky=tk.NE,pady=6)
		self.saveResultsLabel = tk.Label(self.f_setup,text='Work Folder:')
		self.saveResultsLabel.grid(in_=self.f_setup,column=0,row=2,sticky=tk.NE,pady=6)
		self.targetFilesLabel = tk.Label(self.f_setup,text='Target Files:')
		self.targetFilesLabel.grid(in_=self.f_setup,column=0,row=3,rowspan=2,sticky=tk.NE)
		self.componentFilesLabel = tk.Label(self.f_setup,text="Component\nFolders:",justify=tk.RIGHT)
		self.componentFilesLabel.grid(in_=self.f_setup,column=0,row=5,rowspan=2,sticky=tk.NE)

		self.runTitleEntry = tk.Entry(self.f_setup,width=20,textvariable=self.runTitle)
		self.runTitleEntry.grid(in_=self.f_setup,column=1,row=1,sticky=tk.W)
		self.saveResultsEntry = tk.Entry(self.f_setup,width=20,textvariable=self.saveResults)
		self.saveResultsEntry.grid(in_=self.f_setup,column=1,row=2,sticky=tk.W)

		self.targetFilesList = tk.Listbox(self.f_setup,width=23,height=4,listvariable=self.targetFiles,selectmode=tk.BROWSE)
		self.targetFilesList.grid(in_=self.f_setup,column=1,row=3,rowspan=2,sticky=tk.W,padx=2,pady=4)
		self.targetFilesList.bind('<<ListboxSelect>>',self.setListStates)
		self.targetFilesScroll = tk.Scrollbar(self.f_setup,orient=tk.VERTICAL)
		self.targetFilesScroll.grid(in_=self.f_setup,column=2,row=3,rowspan=2,sticky=tk.W+tk.N+tk.S,pady=4)
		self.targetFilesList.config(yscrollcommand=self.targetFilesScroll.set)
		self.targetFilesScroll.config(command=self.targetFilesList.yview)

		self.componentFilesList = tk.Listbox(self.f_setup,width=23,height=4,listvariable=self.componentFiles,selectmode=tk.BROWSE)
		self.componentFilesList.grid(in_=self.f_setup,column=1,row=5,rowspan=2,sticky=tk.W,padx=2,pady=4)
		self.componentFilesList.bind('<<ListboxSelect>>',self.setListStates)
		self.componentFilesScroll = tk.Scrollbar(self.f_setup,orient=tk.VERTICAL)
		self.componentFilesScroll.grid(in_=self.f_setup,column=2,row=5,rowspan=2,sticky=tk.W+tk.N+tk.S,pady=4)
		self.componentFilesList.config(yscrollcommand=self.componentFilesScroll.set)
		self.componentFilesScroll.config(command=self.componentFilesList.yview)

		self.setResultsPathButton = tk.Button(self.f_setup, text='Set...', command=self.setResultsPath)
		self.setResultsPathButton.grid(in_=self.f_setup,column=3,row=2,sticky=tk.W)
		self.addTargetButton = tk.Button(self.f_setup, text='Add...', command=self.addTargetFile)
		self.addTargetButton.grid(in_=self.f_setup,column=3,row=3,sticky=tk.SW)
		self.removeTargetButton = tk.Button(self.f_setup, text='Remove', command=self.delTargetFile,state=tk.DISABLED)
		self.removeTargetButton.grid(in_=self.f_setup,column=3,row=4,sticky=tk.NW)
		self.addComponentButton = tk.Button(self.f_setup, text='Add...', command=self.addComponentDir)
		self.addComponentButton.grid(in_=self.f_setup,column=3,row=5,sticky=tk.SW)
		self.removeComponentButton = tk.Button(self.f_setup, text='Remove', command=self.delComponentDir,state=tk.DISABLED)
		self.removeComponentButton.grid(in_=self.f_setup,column=3,row=6,sticky=tk.NW)

		#
		self.f_algorithm = tk.LabelFrame(self, borderwidth=2, width=200, height=170, relief='groove', text='Genetic Algorithm')
		self.f_algorithm.grid(column=2,row=0,columnspan=2)
		self.f_algorithm.grid_propagate(0)

		self.ensembleSizeLabel = tk.Label(self.f_algorithm,text='Ensemble Size:')
		self.ensembleSizeLabel.grid(in_=self.f_algorithm,column=0,row=0,sticky=tk.E)
		self.numEnsemblesLabel = tk.Label(self.f_algorithm,text='Number of Ensembles:')
		self.numEnsemblesLabel.grid(in_=self.f_algorithm,column=0,row=1,sticky=tk.E)
		self.gCrossFreqLabel = tk.Label(self.f_algorithm,text='Crossing Frequency:')
		self.gCrossFreqLabel.grid(in_=self.f_algorithm,column=0,row=2,sticky=tk.E)
		self.gMutateFreqLabel = tk.Label(self.f_algorithm,text='Mutation Frequency:')
		self.gMutateFreqLabel.grid(in_=self.f_algorithm,column=0,row=3,sticky=tk.E)
		self.gSourceRatioLabel = tk.Label(self.f_algorithm,text='Mutation Source Ratio:')
		self.gSourceRatioLabel.grid(in_=self.f_algorithm,column=0,row=4,sticky=tk.E)

		self.ensembleSizeEntry = tk.Entry(self.f_algorithm,width=4,textvariable=self.ensembleSize)
		self.ensembleSizeEntry.grid(in_=self.f_algorithm,column=1,row=0)
		self.numEnsemblesEntry = tk.Entry(self.f_algorithm,width=4,textvariable=self.numEnsembles)
		self.numEnsemblesEntry.grid(in_=self.f_algorithm,column=1,row=1)
		self.gCrossFreqEntry = tk.Entry(self.f_algorithm,width=4,textvariable=self.gCrossFreq)
		self.gCrossFreqEntry.grid(in_=self.f_algorithm,column=1,row=2)
		self.gMutateFreqEntry = tk.Entry(self.f_algorithm,width=4,textvariable=self.gMutateFreq)
		self.gMutateFreqEntry.grid(in_=self.f_algorithm,column=1,row=3)
		self.gSourceRatioEntry = tk.Entry(self.f_algorithm,width=4,textvariable=self.gSourceRatio)
		self.gSourceRatioEntry.grid(in_=self.f_algorithm,column=1,row=4)

		#
		self.f_convergence = tk.LabelFrame(self, borderwidth=2, width=200, height=110, relief='groove', text='Convergence Criterion')
		self.f_convergence.grid(column=2,row=1,columnspan=2)
		self.f_convergence.grid_propagate(0)

		self.minFitnessLabel = tk.Label(self.f_convergence,text='Minimum Fitness:')
		self.minFitnessLabel.grid(in_=self.f_convergence,column=0,row=0,sticky=tk.E)
		self.minRSDLabel = tk.Label(self.f_convergence,text='Minimum RSD:')
		self.minRSDLabel.grid(in_=self.f_convergence,column=0,row=1,sticky=tk.E)
		self.maxGenerationsLabel = tk.Label(self.f_convergence,text='Max. Generations:')
		self.maxGenerationsLabel.grid(in_=self.f_convergence,column=0,row=2,sticky=tk.E)

		self.minFitnessEntry = tk.Entry(self.f_convergence,width=4,textvariable=self.minFitness)
		self.minFitnessEntry.grid(in_=self.f_convergence,column=1,row=0,sticky=tk.W)
		self.minRSDEntry = tk.Entry(self.f_convergence,width=4,textvariable=self.minRSD)
		self.minRSDEntry.grid(in_=self.f_convergence,column=1,row=1,sticky=tk.W)
		self.maxGenerationsEntry = tk.Entry(self.f_convergence,width=4,textvariable=self.maxGenerations)
		self.maxGenerationsEntry.grid(in_=self.f_convergence,column=1,row=2,sticky=tk.W)

		self.minFitnessBox = tk.Checkbutton(self.f_convergence,variable=self.minFitnessCheck,command=self.setCheckboxStates)
		self.minFitnessBox.grid(in_=self.f_convergence,column=2,row=0,sticky=tk.W)
		self.minRSDBox = tk.Checkbutton(self.f_convergence,variable=self.minRSDCheck,command=self.setCheckboxStates)
		self.minRSDBox.grid(in_=self.f_convergence,column=2,row=1,sticky=tk.W)
		self.maxGenerationsBox = tk.Checkbutton(self.f_convergence,variable=self.maxGenerationsCheck,command=self.setCheckboxStates)
		self.maxGenerationsBox.grid(in_=self.f_convergence,column=2,row=2,sticky=tk.W)

		#
		self.f_output = tk.LabelFrame(self, borderwidth=2, width=260, height=150, relief='groove', text='Output')
		self.f_output.grid(column=0,row=2,pady=0,sticky=tk.NW)
		self.f_output.grid_propagate(0)

		self.bestFitLabel = tk.Label(self.f_output,text='Best-fit ensemble:')
		self.bestFitLabel.grid(in_=self.f_output,column=0,row=0,sticky=tk.E)
		self.componentStatsLabel = tk.Label(self.f_output,text='Component statistics:')
		self.componentStatsLabel.grid(in_=self.f_output,column=0,row=1,sticky=tk.E)
		self.componentCorrsLabel = tk.Label(self.f_output,text='Component correlations:')
		self.componentCorrsLabel.grid(in_=self.f_output,column=0,row=2,sticky=tk.E)
		self.pluginExtrasLabel = tk.Label(self.f_output,text='Plugin extras (fits, etc.):')
		self.pluginExtrasLabel.grid(in_=self.f_output,column=0,row=3,sticky=tk.E)
		self.optimizationStateLabel = tk.Label(self.f_output,text='Optimization state:')
		self.optimizationStateLabel.grid(in_=self.f_output,column=0,row=4,sticky=tk.E)

		self.bestFitBox = tk.Checkbutton(self.f_output,variable=self.bestFitCheck,command=self.setCheckboxStates)
		self.bestFitBox.grid(in_=self.f_output,column=1,row=0,sticky=tk.W)
		self.componentStatsBox = tk.Checkbutton(self.f_output,variable=self.componentStatsCheck,command=self.setCheckboxStates,state=tk.DISABLED)
		self.componentStatsBox.grid(in_=self.f_output,column=1,row=1,sticky=tk.W)
		self.componentCorrsBox = tk.Checkbutton(self.f_output,variable=self.componentCorrCheck,command=self.setCheckboxStates,state=tk.DISABLED)
		self.componentCorrsBox.grid(in_=self.f_output,column=1,row=2,sticky=tk.W)
		self.pluginExtrasBox = tk.Checkbutton(self.f_output,variable=self.pluginExtrasCheck,command=self.setCheckboxStates)
		self.pluginExtrasBox.grid(in_=self.f_output,column=1,row=3,sticky=tk.W)
		self.optimizationStateBox = tk.Checkbutton(self.f_output,variable=self.optimizationStateCheck,command=self.setCheckboxStates)
		self.optimizationStateBox.grid(in_=self.f_output,column=1,row=4,sticky=tk.W)

		self.optCutoffLabel = tk.Label(self.f_output,text='Cutoff:')
		self.optCutoffLabel.grid(in_=self.f_output,column=2,row=0,sticky=tk.S)
		self.componentStatsEntry = tk.Entry(self.f_output,width=4,textvariable=self.componentStats)
		self.componentStatsEntry.grid(in_=self.f_output,column=2,row=1,stick=tk.W)
		self.componentCorrsEntry = tk.Entry(self.f_output,width=4,textvariable=self.componentCorr)
		self.componentCorrsEntry.grid(in_=self.f_output,column=2,row=2,stick=tk.W)

		self.componentStatsPct = tk.Label(self.f_output,text='%')
		self.componentStatsPct.grid(in_=self.f_output,column=3,row=1,sticky=tk.W)
		self.componentCorrsPct = tk.Label(self.f_output,text='%')
		self.componentCorrsPct.grid(in_=self.f_output,column=3,row=2,sticky=tk.W)

		#
		self.f_optimization = tk.LabelFrame(self, borderwidth=2, width=210, height=150, relief='groove', text='Ratio Optimization')
		self.f_optimization.grid(column=1,row=2,columnspan=2,padx=4,pady=0)
		self.f_optimization.grid_propagate(0)

		self.optMethodLabel = tk.Label(self.f_optimization,text='Optimization Method:')
		self.optMethodLabel.grid(in_=self.f_optimization,column=0,row=0,sticky=tk.W)
		self.optToleranceLabel = tk.Label(self.f_optimization,text='Convergence tolerance:')
		self.optToleranceLabel.grid(in_=self.f_optimization,column=0,row=2,sticky=tk.E)
		self.optIterationsLabel = tk.Label(self.f_optimization,text='Maximum iterations:')
		self.optIterationsLabel.grid(in_=self.f_optimization,column=0,row=3,sticky=tk.E)

		self.optMethodOptionMenu = tk.OptionMenu(self.f_optimization,self.optMethodOption,*self.optMethodOptions)
		self.optMethodOptionMenu.grid(in_=self.f_optimization,column=0,row=1,columnspan=2,sticky=tk.W)

		self.optToleranceEntry = tk.Entry(self.f_optimization,width=4,textvariable=self.optTolerance)
		self.optToleranceEntry.grid(in_=self.f_optimization,column=1,row=2,sticky=tk.W)
		self.optIterationsEntry = tk.Entry(self.f_optimization,width=4,textvariable=self.optIterations)
		self.optIterationsEntry.grid(in_=self.f_optimization,column=1,row=3,sticky=tk.W)

		#
		self.f_buttons = tk.Frame(self, width=120, height=110 )
		self.f_buttons.grid(column=3,row=2,padx=4,ipady=10)
		self.f_buttons.grid_propagate(0)

		self.sConfigButton = tk.Button(self.f_buttons, text='Load Config...', command=lambda:loadControlVarArgs(self) )
		self.sConfigButton.grid(in_=self.f_buttons,column=0,row=0,sticky=tk.S)
		self.sConfigButton = tk.Button(self.f_buttons, text='Save Config...', command=lambda:saveControlVarArgs(self) )
		self.sConfigButton.grid(in_=self.f_buttons,column=0,row=1,sticky=tk.N)
		self.startButton = tk.Button(self.f_buttons, text='Start Run',default=tk.ACTIVE,state=tk.DISABLED, command=self.setupAndStartRun )
		self.startButton.grid(in_=self.f_buttons,column=0,row=2,pady=4,sticky=tk.S)
		self.closeButton = tk.Button(self.f_buttons, text='Cancel', command=self.close)
		self.closeButton.grid(in_=self.f_buttons,column=0,row=3,pady=4,sticky=tk.N)
