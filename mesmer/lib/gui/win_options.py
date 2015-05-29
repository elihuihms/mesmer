import Tkinter as tk
import argparse

from tools_TkTooltip import ToolTip

class OptionsWindow(tk.Frame):
	def __init__(self, master, options):
		self.master = master
		self.master.title('Set Options')
		self.master.resizable(width=False, height=False)

		self.master.protocol('WM_DELETE_WINDOW', self.saveWindow)
		self.master.bind("<Return>", self.saveWindow)

		self.options = options

		tk.Frame.__init__(self,master)

		self.grid()
		self.createWidgets()
		self.returncode = 0

	def saveWindow(self, evt=None):
		for i,option in enumerate(self.options):
			try:
				option['value'] = self.optionValues[i].get()
			except ValueError:
				option['value'] = None
		self.returncode = 0
		self.close()

	def close(self):
		self.master.destroy()

	def cancelWindow(self):
		self.returncode = 1
		self.close()
		
	def createWidgets(self):
		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		self.optionGroups	= {}
		self.optionLabels	= []
		self.optionToolTips	= []
		self.optionValues	= []
		self.optionEntries	= []

		self.optionGroups[''] = tk.Frame(self.container,border=0)
		self.optionGroups[''].grid(in_=self.container,column=0,row=0,columnspan=2,sticky=tk.W)
		for option in self.options:
			if option['group'] == 'optional arguments':
				option['group'] = ''
			if option['group'] not in self.optionGroups:
				self.optionGroups[option['group']] = tk.LabelFrame(self.container,text=option['group'])
				self.optionGroups[option['group']].grid(in_=self.container,column=0,row=len(self.optionGroups),columnspan=2,sticky=tk.W)
				
		for option in self.options:
			container = self.optionGroups[option['group']]
			row = len(container.winfo_children())/2
			self.optionLabels.append( tk.Label(container,text=option['dest']) )
			self.optionLabels[-1].grid(in_=container,column=0,row=row,sticky=tk.W)
			self.optionToolTips.append( ToolTip(self.optionLabels[-1],follow_mouse=0,text=option['help']) )

			if(option['choices'] != None):
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.OptionMenu(container,self.optionValues[-1],*option['choices']) )
			elif(option['nargs'] == 0):
				self.optionValues.append( tk.IntVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.Checkbutton(container,variable=self.optionValues[-1]) )
			elif(option['type'] == type(0)):
				self.optionValues.append( tk.IntVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=4) )
			elif(option['type'] == type(0.0)):
				self.optionValues.append( tk.DoubleVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=8) )
			else:
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(container,textvariable=self.optionValues[-1],width=12) )
			self.optionEntries[-1].grid(in_=container,column=1,row=row,sticky=tk.W)

		self.cancelButton = tk.Button(self.container,text='Cancel',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,row=len(self.optionGroups)+1,sticky=tk.E,pady=(8,0))
		self.saveButton = tk.Button(self.container,text='Apply',command=self.saveWindow,width=8,default=tk.ACTIVE)
		self.saveButton.grid(in_=self.container,row=len(self.optionGroups)+1,column=1,sticky=tk.W,pady=(8,0))