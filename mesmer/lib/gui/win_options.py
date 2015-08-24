import os
import argparse
import Tkinter as tk
import tkFileDialog

from tools_general	import askOpenFilename
from tools_TkTooltip import ToolTip

# Argument groups to not show in the window
_OPTION_HIDE_ARGUMENT_GROUPS = ('CLI-only arguments','CLI arguments')

# Empty argument values
_OPTION_EMPTY_VALUES = ('',None,'None')

# Metavar values to trigger file browser
_OPTION_FILE_METAVARS = ('FILE',)

# Metavar values to trigger directory browser
_OPTION_DIR_METAVARS = ('DIR',)

class OptionsWindow(tk.Frame):
	def __init__(self, master, options):
		self.master = master
		self.master.title('Set Options')
		self.master.resizable(width=False, height=False)

		self.master.protocol('WM_DELETE_WINDOW', self.saveWindow)
		self.master.bind("<Return>", self.saveWindow)

		self.options = options
		self.option_keys = options.keys()
		
		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=6)
		self.pack_propagate(True)
		
		self.createWidgets()
		self.returncode = 0

	def saveWindow(self, evt=None):
		for i,k in enumerate(self.options):
					
			if self.options[k]['group'] in _OPTION_HIDE_ARGUMENT_GROUPS:
				break
				
			try:
				self.options[k]['value'] = self.optionValues[i].get()
			except ValueError:
				self.options[k]['value'] = None
				
			if self.options[k]['value'] in _OPTION_EMPTY_VALUES:
				self.options[k]['value'] == None
			
		self.returncode = 0
		self.close()

	def close(self):
		self.master.destroy()

	def cancel(self):
		self.returncode = 1
		self.close()
		
	def updateFileButton(self, evt):
		for i,b in enumerate(self.optionEntries):
			if b == evt.widget:
				break
		tmp = askOpenFilename(parent=self.master,title=self.options[self.option_keys[i]]['dest'],message=self.options[self.option_keys[i]]['help'])
		self.optionValues[i].set(tmp)
		self.optionEntries[i].config(text=os.path.basename(tmp))
				
	def updateDirButton(self, evt):
		for i,b in enumerate(self.optionEntries):
			if b == evt.widget:
				break
		tmp = tkFileDialog.askdirectory(parent=self.master,title=self.options[self.option_keys[i]]['help'])
		self.optionValues[i].set(tmp)
		self.optionEntries[i].config(text=os.path.basename(os.path.normpath(tmp)))

	def createWidgets(self):
		self.container = tk.Frame(self)
		self.container.grid(padx=6,pady=6)

		self.optionGroups	= {}
		self.optionLabels	= []
		self.optionToolTips	= []
		self.optionValues	= []
		self.optionEntries	= []

		self.optionGroups[''] = tk.Frame(self.container,border=0)
		self.optionGroups[''].grid(column=0,row=0,columnspan=2,sticky=tk.W)
		
		# create option groups beforehand
		for k,option in self.options.iteritems():
			if option['group'] in _OPTION_HIDE_ARGUMENT_GROUPS:
				break

			if option['group'] == 'optional arguments':
				option['group'] = ''
			if option['group'] not in self.optionGroups:
				self.optionGroups[option['group']] = tk.LabelFrame(self.optionGroups[''],text=option['group'])
		
		rowcounter = 0	
		for k,option in self.options.iteritems():
			if option['group'] in _OPTION_HIDE_ARGUMENT_GROUPS:
				break
			if option['value'] in _OPTION_EMPTY_VALUES:
				option['value'] = option['default']

			container = self.optionGroups[option['group']]
			if len(container.winfo_children()) == 0: # group hasn't been placed in window yet
				container.grid(column=0,row=rowcounter,columnspan=2,sticky=tk.W+tk.E)
				rowcounter+=1
				
			# what do we show for the entry label?	
			if option['metavar'] in _OPTION_FILE_METAVARS:
				text = option['dest'][0].upper()+option['dest'][1:]+" file:"
			elif option['metavar'] in _OPTION_DIR_METAVARS:
				text = option['dest'][0].upper()+option['dest'][1:]+" folder:"
			elif option['metavar'] == None:
				text = option['dest'][0].upper()+option['dest'][1:]
			else:
				text = option['metavar']
	
			self.optionLabels.append( tk.Label(container,text=text) )
			self.optionLabels[-1].grid(column=0,row=rowcounter,sticky=tk.W)
			self.optionToolTips.append( ToolTip(self.optionLabels[-1],follow_mouse=0,text=option['help']) )

			# file input are handled a bit differently
			if option['metavar'] in _OPTION_FILE_METAVARS: #file
				rowcounter+=1
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.Button(container,text=os.path.basename(str(option['value'])),justify=tk.LEFT) )
				self.optionEntries[-1].bind('<ButtonRelease-1>',self.updateFileButton)
				self.optionEntries[-1].grid(column=0,columnspan=2,row=rowcounter,sticky=tk.W+tk.E)
				rowcounter+=1
				continue

			elif option['metavar'] in _OPTION_DIR_METAVARS: #directory
				rowcounter+=1
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.Button(container,text=os.path.basename(os.path.normpath(str(option['value']))),justify=tk.LEFT) )
				self.optionEntries[-1].bind('<ButtonRelease-1>',self.updateDirButton)
				self.optionEntries[-1].grid(column=0,columnspan=2,row=rowcounter,sticky=tk.W+tk.E)
				rowcounter+=1
				continue

			elif(option['choices'] != None): #multiple choice
				self.optionValues.append( tk.StringVar() )
				self.optionEntries.append( tk.OptionMenu(container,self.optionValues[-1],*option['choices']) )
				self.optionEntries[-1].config(width=12)
				if option['value'] not in option['choices']:
					option['value'] = option['default']
			elif(option['nargs'] == 0): #boolean
				self.optionValues.append( tk.IntVar() )
				self.optionEntries.append( tk.Checkbutton(container,variable=self.optionValues[-1]) )
			elif(option['type'] == type(0)): #int
				self.optionValues.append( tk.IntVar() )
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=4) )
			elif(option['type'] == type(0.0)): #float
				self.optionValues.append( tk.DoubleVar() )
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=8) )
			else: #string
				self.optionValues.append( tk.StringVar() )
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=12) )

			self.optionValues[-1].set( option['value'] )
			self.optionEntries[-1].grid(column=1,row=rowcounter,sticky=tk.W)
			rowcounter+=1

		self.cancelButton = tk.Button(self.container,text='Cancel',command=self.cancel)
		self.cancelButton.grid(column=0,row=rowcounter,sticky=tk.E,pady=(8,0))
		self.saveButton = tk.Button(self.container,text='Apply',command=self.saveWindow,width=8,default=tk.ACTIVE)
		self.saveButton.grid(column=1,row=rowcounter,sticky=tk.W,pady=(8,0))