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
		# retrieve the set values, save back to the options dict
		for (i,k) in enumerate(sorted( self.options.keys() )):
			try:
				self.options[k]['value'] = self.optionValues[i].get()
			except:
				self.options[k]['value'] = None

		self.close()

	def close(self):
		self.master.destroy()

	def cancelWindow(self):
		self.returncode = 1
		self.close()
		
	def createWidgets(self):
		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		self.optionLabels	= []
		self.optionToolTips	= []
		self.optionValues	= []
		self.optionEntries	= []

		rowCounter = 0
		for k in sorted( self.options.keys() ):
			option = self.options[k]
			
			self.optionLabels.append( tk.Label(self.container,text=option['dest']) )
			self.optionLabels[-1].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.optionToolTips.append( ToolTip(self.optionLabels[-1],follow_mouse=0,text=option['help']) )

			if(option['choices'] != None):
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.OptionMenu(self.container,self.optionValues[-1],*option['choices']) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			elif(option['nargs'] == 0):
				self.optionValues.append( tk.IntVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.Checkbutton(self.container,variable=self.optionValues[-1]) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			elif(option['type'] == type(0)):
				self.optionValues.append( tk.IntVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(self.container,textvariable=self.optionValues[-1],width=4) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			elif(option['type'] == type(0.0)):
				self.optionValues.append( tk.DoubleVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(self.container,textvariable=self.optionValues[-1],width=8) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			else:
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(self.container,textvariable=self.optionValues[-1],width=12) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			rowCounter+=1

		self.cancelButton = tk.Button(self.container,text='Cancel',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,row=rowCounter,sticky=tk.E,pady=(8,0))
		self.saveButton = tk.Button(self.container,text='Apply',command=self.saveWindow,width=8,default=tk.ACTIVE)
		self.saveButton.grid(in_=self.container,row=rowCounter,column=1,sticky=tk.W,pady=(8,0))