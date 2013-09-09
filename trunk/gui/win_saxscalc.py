import os
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import shelve

from gui.tools_TkTooltip	import ToolTip
from gui.tools_general		import getWhichPath
from gui.tools_saxscalc		import calcSAXSFromWindow

class SAXSCalcWindow(tk.LabelFrame):
	def __init__(self, master, pdbList, callback=None):
		self.master = master
		self.pdbList = pdbList
		self.callback = callback
		self.master.resizable(width=False, height=False)
		self.master.title('Calculate SAXS Profiles')

		tk.LabelFrame.__init__(self,master,width=360,height=150,borderwidth=0)
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

	def startCalc(self):
		self.SAXSCalcCounter.set(0)
		dir = calcSAXSFromWindow(self)

	def cancelCalc(self):
		if(self.SAXSCalcAfterID):
			self.after_cancel( self.SAXSCalcAfterID )
		self.closeWindow()

	def updateParent(self,dir):
		if(self.callback):
			self.callback(dir)

	def closeWindow(self):
		self.master.destroy()

	def createControlVars(self):
		self.SAXSCalcPath		= tk.StringVar()
		if(self.prefs.has_key('saxs_calc_path')):
			self.SAXSCalcPath.set( self.prefs['saxs_calc_path'] )
		else:
			self.SAXSCalcPath.set( getWhichPath('crysol') )

		self.SAXSCalcArgs		= tk.StringVar()
		if( self.SAXSCalcPath.get()[-6:] == 'crysol' ):
			self.SAXSCalcArgs.set("-ns 128 -sm 0.5")
		elif( self.SAXSCalcPath.get()[-4:] == 'foxs' ):
			self.SAXSCalcArgs.set("-s 128 -q 0.5")

		self.SAXSCalcAfterID	= None
		self.SAXSCalcProgress	= tk.StringVar()
		self.SAXSCalcProgress.set("Progress: 0/%i" % (len(self.pdbList)) )
		self.SAXSCalcCounter	= tk.IntVar()
		self.SAXSCalcCounter.set(0)

	def createToolTips(self):
		#self.createTargetTT 	= ToolTip(self.createTargetButton,		follow_mouse=0,text='Create a target file from experimental data')
		pass

	def createWidgets(self):
		self.container = tk.Frame(self,borderwidth=0)
		self.container.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.SAXSCalcPathLabel = tk.Label(self.container, text='SAXS profile calculator:')
		self.SAXSCalcPathLabel.grid(in_=self.container,column=0,row=0,columnspan=3,sticky=tk.W)
		self.SAXSCalcPathEntry = tk.Entry(self.container,width=40,textvariable=self.SAXSCalcPath)
		self.SAXSCalcPathEntry.grid(in_=self.container,column=0,row=1,columnspan=3,sticky=tk.E)

		self.SAXSCalcArgsLabel = tk.Label(self.container, text='Program arguments:')
		self.SAXSCalcArgsLabel.grid(in_=self.container,column=0,row=2,columnspan=3,sticky=tk.W)
		self.SAXSCalcArgsEntry = tk.Entry(self.container,width=40,textvariable=self.SAXSCalcArgs)
		self.SAXSCalcArgsEntry.grid(in_=self.container,column=0,row=3,columnspan=3,sticky=tk.E)

		self.SAXSCalcProgressLabel = tk.Label(self.container,textvariable=self.SAXSCalcProgress)
		self.SAXSCalcProgressLabel.grid(in_=self.container,column=0,row=4,sticky=tk.E+tk.W)

		self.cancelButton = tk.Button(self.container, text='Cancel',command=self.cancelCalc)
		self.cancelButton.grid(in_=self.container,column=1,row=4,sticky=tk.E,pady=10)
		self.calcButton = tk.Button(self.container, text='Calculate...',command=self.startCalc,default=tk.ACTIVE)
		self.calcButton.grid(in_=self.container,column=2,row=4,sticky=tk.W,pady=10)
