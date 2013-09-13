import os
import shelve
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import copy

from lib.functions 			import get_input_blocks
from gui.tools_TkTooltip	import ToolTip
from gui.tools_target		import makeTargetFromWindow,setBlockOptions,getPluginOptions
from gui.win_options		import OptionsWindow

class TargetWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.geometry('720x180+100+100')
		self.master.title('Target Builder')
		self.master.resizable(width=False, height=False)

		tk.Frame.__init__(self,master,width=720,height=180)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()
		self.loadPlugins()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()
		self.updateWidgets()

		self.Ready = False

	def loadPrefs(self):
		try:
			self.prefs = shelve.open( os.path.join(os.getcwd(),'gui','preferences') )
		except:
			tkMessageBox.showerror("Error",'Cannot read or create preferences file. Perhaps MESMER is running in a read-only directory?',parent=self)
			self.master.destroy()

	def loadPlugins(self):
		try:
			(self.plugin_types,self.plugin_options) = getPluginOptions(os.path.dirname(os.path.realpath(__file__)))
		except:
			tkMessageBox.showerror("Error",'Cannot load MESMER plugins.',parent=self)
			self.master.destroy()

	def openOptionsWindow(self, evt):
		for (i,w) in enumerate(self.widgetRowOptButtons):
			if w == evt.widget:
				break

		type = self.widgetRowTypes[i].get()
		self.newWindow = tk.Toplevel(self)
		self.optWindow = OptionsWindow(self.newWindow,i,self.widgetRowOptions[i][type],self.setOptionsFromWindow)
		self.newWindow.focus_set()
		self.newWindow.grab_set()
		self.newWindow.transient(self)
		self.newWindow.wait_window(self.newWindow)

	def saveTarget(self):
		name = self.targetName.get().replace(' ','_')
		text = makeTargetFromWindow(self)
		if(text == None):
			return
		tmp = tkFileDialog.asksaveasfile(defaultextension='.target',initialfile="%s.target"%(name),parent=self)
		if(tmp != None):
			tmp.write(text)
			tmp.close()

	def loadTarget(self):
		tmp = tkMessageBox.askquestion("Load Target","Are you sure you would like to load an existing target as a template?\nThis will clear your current entries.", icon='warning',parent=self)
		if(tmp != 'yes'):
			return
		tmp = tkFileDialog.askopenfilename(title='Select target file:',parent=self)
		if(tmp == ''):
			return
		blocks = get_input_blocks(tmp)
		if(len(blocks)<2):
			return

		# remove existing rows
		for i in range(self.rowCounter):
			self.widgetRowChecks[i].set(1)
		self.destroyWidgetRows()

		for b in blocks:
			type = b['type'][0:4]
			header = b['header'].split()
			if(type == 'NAME'):
				self.targetName.set(header[1])
			elif type in self.types.keys():
				self.createWidgetRow()
				self.widgetRowTypes[-1].set( type )
				self.widgetRowWeights[-1].set( header[1] )
				self.widgetRowOptions[-1] = setOptsFromBlock(self.widgetRowOptions[-1],b)

	def setOptionsFromWindow(self, index, spec ):
		type = self.widgetRowTypes[index].get()
		self.widgetRowOptions[index][type] = spec

	def updateWidgets(self, evt=None):
		self.Ready = True

		for i in range(self.rowCounter):
			type = self.widgetRowTypes[i].get()
			opts = self.widgetRowOptions[i][type]
			if(len(opts['bool_options'])>0 or len(opts['int_options'])>0 or len(opts['float_options'])>0 or len(opts['string_options'])>0):
				self.widgetRowOptButtons[i].config(state=tk.NORMAL)
			else:
				self.widgetRowOptButtons[i].config(state=tk.DISABLED)

			if(self.widgetRowFiles[i].get() == ''):
				self.Ready = False

		if(self.targetName.get() == ''):
			self.Ready = False

		if(self.Ready):
			self.saveButton.config(state=tk.ACTIVE)
		else:
			self.saveButton.config(state=tk.DISABLED)

	def attachDataFile(self,evt):
		tmp = tkFileDialog.askopenfilename(title='Select experimental datafile:',parent=self)
		if(tmp == ''):
			return
		for (i,w) in enumerate(self.widgetRowFileButtons):
			if w == evt.widget:
				break
		self.widgetRowFiles[i].set(tmp)
		self.updateWidgets()

	def closeWindow(self):
		self.master.destroy()

	def createToolTips(self):
		#self.createTargetTT 	= ToolTip(self.createTargetButton,		follow_mouse=0,text='Create a target file from experimental data')
		pass

	def createControlVars(self):
		self.targetName			= tk.StringVar()
		self.targetComments		= tk.StringVar()
		self.widgetRowChecks = []
		self.widgetRowTypes = []
		self.widgetRowTypeOptions = []
		self.widgetRowWeights = []
		self.widgetRowFiles = []
		self.widgetRowOptions = []

	def createWidgets(self):
		self.f_header = tk.LabelFrame(self,text='General Info')
		self.f_header.grid(in_=self,row=0,sticky=tk.W,ipady=4,ipadx=8,padx=8)

		self.targetNameLabel = tk.Label(self.f_header,text='Name:')
		self.targetNameLabel.grid(in_=self.f_header,column=0,row=0,sticky=tk.E)
		self.targetNameEntry = tk.Entry(self.f_header,textvariable=self.targetName)
		self.targetNameEntry.grid(in_=self.f_header,column=1,row=0,sticky=tk.W)
		self.targetNameEntry.bind("<Key>",self.updateWidgets)

		self.targetCommentsLabel = tk.Label(self.f_header,text='Comments:')
		self.targetCommentsLabel.grid(in_=self.f_header,column=2,row=0,sticky=tk.E)
		self.targetCommentsEntry = tk.Entry(self.f_header,textvariable=self.targetComments,width=36)
		self.targetCommentsEntry.grid(in_=self.f_header,column=3,row=0,sticky=tk.W)

		self.f_container = tk.LabelFrame(self,borderwidth=2,relief='groove',text='Experimental Data')
		self.f_container.grid(in_=self,sticky=tk.W,ipady=4,ipadx=8,padx=8)

		self.addRowButton = tk.Button(self.f_container,text='Add',command=self.createWidgetRow)
		self.addRowButton.grid(in_=self.f_container,column=0,row=0,sticky=tk.E)
		self.delRowButton = tk.Button(self.f_container,text='Remove',command=self.destroyWidgetRows)
		self.delRowButton.grid(in_=self.f_container,column=1,row=0,sticky=tk.W)

		self.rowHeaderSelectLabel = tk.Label(self.f_container,text='Select')
		self.rowHeaderSelectLabel.grid(in_=self.f_container,column=0,row=1)
		self.rowHeaderTypeLabel = tk.Label(self.f_container,text='Type')
		self.rowHeaderTypeLabel.grid(in_=self.f_container,column=1,row=1)
		self.rowHeaderWeightLabel = tk.Label(self.f_container,text='Weight')
		self.rowHeaderWeightLabel.grid(in_=self.f_container,column=2,row=1,sticky=tk.W)
		self.rowHeaderFileLabel = tk.Label(self.f_container,text='File Path')
		self.rowHeaderFileLabel.grid(in_=self.f_container,column=3,row=1,sticky=tk.W)

		self.rowCounter = 0
		self.widgetRowCheckboxes = []
		self.widgetRowTypeMenus = []
		self.widgetRowWeightEntries = []
		self.widgetRowFileEntries = []
		self.widgetRowFileButtons = []
		self.widgetRowOptButtons = []
		self.createWidgetRow()

		self.f_footer = tk.Frame(self,borderwidth=0)
		self.f_footer.grid(in_=self,row=2)

		self.openButton = tk.Button(self.f_footer,text='Load Target...',command=self.loadTarget)
		self.openButton.grid(in_=self.f_footer,column=0,row=0,sticky=tk.N+tk.S+tk.E,pady=8)
		self.saveButton = tk.Button(self.f_footer,text='Save Target...',command=self.saveTarget,default=tk.ACTIVE)
		self.saveButton.grid(in_=self.f_footer,column=1,row=0,sticky=tk.N+tk.S+tk.W,pady=8)
		self.cancelButton = tk.Button(self.f_footer,text='Cancel',command=self.closeWindow)
		self.cancelButton.grid(in_=self.f_footer,column=2,row=0,sticky=tk.N+tk.S+tk.E,pady=8,padx=20)

	def createWidgetRow(self):
		self.rowCounter+=1

		# append a copy of the plugin options for the default type

		self.widgetRowOptions.append( convertParserToOptions )

		self.widgetRowChecks.append( tk.IntVar() )
		self.widgetRowCheckboxes.append( tk.Checkbutton(self.f_container,variable=self.widgetRowChecks[-1]) )
		self.widgetRowCheckboxes[-1].grid(in_=self.f_container,column=0,row=self.rowCounter+1)

		self.widgetRowTypeOptions.append( self.types.keys() )
		self.widgetRowTypes.append( tk.StringVar() )
		self.widgetRowTypes[-1].set( self.types.keys()[0] )
		self.widgetRowTypeMenus.append( tk.OptionMenu(self.f_container,self.widgetRowTypes[-1],*self.widgetRowTypeOptions[-1],command=self.updateWidgets) )
		self.widgetRowTypeMenus[-1].grid(in_=self.f_container,column=1,row=self.rowCounter+1)

		self.widgetRowWeights.append( tk.DoubleVar() )
		self.widgetRowWeights[-1].set( 1.0 )
		self.widgetRowWeightEntries.append( tk.Entry(self.f_container,width=3,textvariable=self.widgetRowWeights[-1]) )
		self.widgetRowWeightEntries[-1].grid(in_=self.f_container,column=2,row=self.rowCounter+1)

		self.widgetRowFiles.append( tk.StringVar() )
		self.widgetRowFileEntries.append( tk.Entry(self.f_container,width=30,textvariable=self.widgetRowFiles[-1]) )
		self.widgetRowFileEntries[-1].grid(in_=self.f_container,column=3,row=self.rowCounter+1)

		self.widgetRowFileButtons.append( tk.Button(self.f_container,text='Attach Data...') )
		self.widgetRowFileButtons[-1].bind('<ButtonRelease-1>',self.attachDataFile)
		self.widgetRowFileButtons[-1].grid(in_=self.f_container,column=4,row=self.rowCounter+1)

		self.widgetRowOptButtons.append( tk.Button(self.f_container,text='Set Options...') )
		self.widgetRowOptButtons[-1].bind('<ButtonRelease-1>',self.openOptionsWindow)
		self.widgetRowOptButtons[-1].grid(in_=self.f_container,column=5,row=self.rowCounter+1)

		self.delRowButton.config(state=tk.NORMAL)

		self.master.geometry('720x%i' % (180+self.rowCounter*30))
		self.config(width=720,height=(180+self.rowCounter*30))

	def destroyWidgetRows(self):
		index=0
		while(index<self.rowCounter):
			if(self.widgetRowChecks[index].get() > 0):
				self.widgetRowCheckboxes[index].destroy()
				self.widgetRowTypeMenus[index].destroy()
				self.widgetRowWeightEntries[index].destroy()
				self.widgetRowFileEntries[index].destroy()
				self.widgetRowFileButtons[index].destroy()
				self.widgetRowOptButtons[index].destroy()
				del self.widgetRowCheckboxes[index]
				del self.widgetRowTypeMenus[index]
				del self.widgetRowWeights[index]
				del self.widgetRowWeightEntries[index]
				del self.widgetRowFileEntries[index]
				del self.widgetRowFileButtons[index]
				del self.widgetRowOptButtons[index]
				del self.widgetRowChecks[index]
				del self.widgetRowTypeOptions[index]
				del self.widgetRowTypes[index]
				del self.widgetRowFiles[index]
				del self.widgetRowOptions[index]
				self.rowCounter-=1
			else:
				index+=1

		if(self.rowCounter==0):
			self.delRowButton.config(state=tk.DISABLED)

		self.master.geometry('720x%i' % (180+self.rowCounter*30))
		self.config(width=720,height=(180+self.rowCounter*30))