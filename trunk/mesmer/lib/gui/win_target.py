import os
import shelve
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import copy

from .. utility_functions 	import get_input_blocks
from tools_TkTooltip		import ToolTip
from tools_plugin			import getTargetPluginOptions,setOptionsFromBlock
from tools_target			import makeTargetFromWindow
from win_options			import OptionsWindow
from tools_general			import openUserPrefs

class TargetWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.geometry('720x180+100+100')
		self.master.title('Target Builder')
		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master,width=720,height=180)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()

		self.createControlVars()
		self.createWidgets()
		self.createToolTips()
		
		# create an initial restraint type
		self.createWidgetRow()

		self.updateWidgets()

	def loadPrefs(self):
		try:
			self.prefs = openUserPrefs()
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()
		
		mesmer_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
		try:
			(self.plugin_types,self.plugin_options) = getTargetPluginOptions(mesmer_base_dir)
		except Exception as e:
			tkMessageBox.showerror("Error",'Failure loading MESMER plugins.\n\nReported error:%s' % e,parent=self)
			self.master.destroy()

	def openOptionsWindow(self, evt):
		# find the row that generated the event
		for (i,w) in enumerate(self.widgetRowOptButtons):
			if w == evt.widget:
				break

		# send the correct set of options to the window
		type = self.widgetRowTypes[i].get()
		for (j,t) in enumerate(self.plugin_types):
			if(type in t):
				break

		self.newWindow = tk.Toplevel(self.master)
		self.optWindow = OptionsWindow(self.newWindow,self.widgetRowOptions[i][j])
		self.newWindow.focus_set()
		self.newWindow.grab_set()
		self.newWindow.transient(self)
		self.newWindow.wait_window(self.newWindow)

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

		# make a list of data types we have plugins for
		available_types = []
		for t in self.plugin_types:
			available_types.extend(t)

		for b in blocks:
			type = b['type'][0:4]
			header = b['header'].split()

			if(type == 'NAME'):
				self.targetName.set(header[1])
			elif(type in available_types):
				self.createWidgetRow()

				# update the new row with the right type and options
				self.widgetRowTypes[-1].set( type )
				self.widgetRowWeights[-1].set( header[1] )

				# set the plugin options for this type of data from the block
				for i in range(len(self.plugin_types)):
					if( type in self.plugin_types[i] ):
						setOptionsFromBlock(self.widgetRowOptions[-1][i],b)

	def updateWidgets(self, evt=None):
		if(self.targetName.get() != ''):
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

	def close(self):
		self.master.destroy()

	def createToolTips(self):
		self.targetNameTT		= ToolTip(self.targetNameEntry, 	follow_mouse=0, text='A simple name for this target. Will be used to identify fitting results.')
		self.targetCommentsTT 	= ToolTip(self.targetCommentsEntry,	follow_mouse=0, text='A comment used to store additional information about this target. Not directly used by MESMER.')
		self.addRowButtonTT 	= ToolTip(self.addRowButton,		follow_mouse=0, text='Append a new experimental data restraint to the target.')
		self.delRowButtonTT 	= ToolTip(self.delRowButton,		follow_mouse=0, text='Remove the selected experimental data restraint(s) from the target.')
		self.openButtonTT	 	= ToolTip(self.openButton,			follow_mouse=0, text='Load an existing MESMER target.')
		self.saveButtonTT	 	= ToolTip(self.saveButton,			follow_mouse=0, text='Save the current target.')
		self.cancelButtonTT	 	= ToolTip(self.cancelButton,		follow_mouse=0, text='Close the window without saving.')
		self.widgetRowCheckboxesTT = []
		self.widgetRowTypeMenusTT = []
		self.widgetRowWeightEntriesTT = []
		self.widgetRowFileEntriesTT = []
		self.widgetRowFileButtonsTT = []
		self.widgetRowOptButtonsTT = []
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

		self.f_footer = tk.Frame(self,borderwidth=0)
		self.f_footer.grid(in_=self,row=2)

		self.openButton = tk.Button(self.f_footer,text='Load Target...',command=self.loadTarget)
		self.openButton.grid(in_=self.f_footer,column=0,row=0,sticky=tk.N+tk.S+tk.E,pady=8)
		self.saveButton = tk.Button(self.f_footer,text='Save Target...',default=tk.ACTIVE,command=lambda: makeTargetFromWindow(self))
		self.saveButton.grid(in_=self.f_footer,column=1,row=0,sticky=tk.N+tk.S+tk.W,pady=8)
		self.cancelButton = tk.Button(self.f_footer,text='Cancel',command=self.close)
		self.cancelButton.grid(in_=self.f_footer,column=2,row=0,sticky=tk.N+tk.S+tk.E,pady=8,padx=20)

	def createWidgetRow(self):
		self.rowCounter+=1

		# append a copy of the options for the available plugins
		self.widgetRowOptions.append( copy.deepcopy(self.plugin_options) )
		available_types = []
		for t in self.plugin_types:
			available_types.extend(t)

		self.widgetRowChecks.append( tk.IntVar() )
		self.widgetRowCheckboxes.append( tk.Checkbutton(self.f_container,variable=self.widgetRowChecks[-1]) )
		self.widgetRowCheckboxes[-1].grid(in_=self.f_container,column=0,row=self.rowCounter+1)

		self.widgetRowTypeOptions.append( available_types )
		self.widgetRowTypes.append( tk.StringVar() )
		self.widgetRowTypes[-1].set( available_types[0] )
		self.widgetRowTypeMenus.append( tk.OptionMenu(self.f_container,self.widgetRowTypes[-1],*available_types,command=self.updateWidgets) )
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
		
		# append tool tips
		self.widgetRowCheckboxesTT.append( ToolTip(self.widgetRowCheckboxes[-1], 	follow_mouse=0, text='Mark restraint for deletion') )
		self.widgetRowTypeMenusTT.append( ToolTip(self.widgetRowTypeMenus[-1], 	follow_mouse=0, text='Set the restraint type') )
		self.widgetRowWeightEntriesTT.append( ToolTip(self.widgetRowWeightEntries[-1], 	follow_mouse=0, text='Sets the relative weighting for this restraint.') )
		self.widgetRowFileEntriesTT.append( ToolTip(self.widgetRowFileEntries[-1], 	follow_mouse=0, text='The path to the experimental data.') )
		self.widgetRowFileButtonsTT.append( ToolTip(self.widgetRowFileButtons[-1], 	follow_mouse=0, text='Sets the path to the experimental data.') )
		self.widgetRowOptButtonsTT.append( ToolTip(self.widgetRowOptButtons[-1], 	follow_mouse=0, text='Sets various fitting and data type options for the restraint.') )

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
				del self.widgetRowCheckboxesTT[index]
				del self.widgetRowTypeMenusTT[index]
				del self.widgetRowWeightEntriesTT[index]
				del self.widgetRowFileEntriesTT[index]
				del self.widgetRowFileButtonsTT[index]
				del self.widgetRowOptButtonsTT[index]
				self.rowCounter-=1
			else:
				index+=1

		if(self.rowCounter==0):
			self.delRowButton.config(state=tk.DISABLED)

		self.master.geometry('720x%i' % (180+self.rowCounter*30))
		self.config(width=720,height=(180+self.rowCounter*30))