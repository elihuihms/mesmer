import Tkinter as tk

from tools_TkTooltip import ToolTip

def setOptsFromBlock( spec, block ):
	type = block['type'][0:4]
	header = block['header'].split()

	for i in range(len(spec[type]['bool_options'])):
		(name,opt,value,help) = spec[type]['bool_options'][i]
		if( ('-%s' % opt) in header[2:] ):
			spec[type]['bool_options'][i] = (name,opt,1,help)
		else:
			spec[type]['bool_options'][i] = (name,opt,0,help)

	for i in range(len(spec[type]['int_options'])):
		(name,opt,value,help) = spec[type]['int_options'][i]
		if( ('-%s' % opt) in header[2:] ):
			spec[type]['int_options'][i] = (name,opt,header.index(('-%s' % opt))+1,help)

	for i in range(len(spec[type]['float_options'])):
		(name,opt,value,help) = spec[type]['float_options'][i]
		if( ('-%s' % opt) in header[2:] ):
			spec[type]['float_options'][i] = (name,opt,header.index(('-%s' % opt))+1,help)

	for i in range(len(spec[type]['string_options'])):
		(name,opt,value,help) = spec[type]['string_options'][i]
		if( ('-%s' % opt) in header[2:] ):
			spec[type]['string_options'][i] = (name,opt,header.index(('-%s' % opt))+1,help)

	return spec

class OptionsWindow(tk.Frame):
	def __init__(self, master, index, spec, callback):
		self.master = master
		self.master.title('Fitting Options')
		#self.master.resizable(width=False, height=False)

		self.index = index
		self.spec = spec
		self.callback = callback

		tk.Frame.__init__(self,master)

		self.grid()
		self.createWidgets()

	def saveWindow(self):

		for i in range(len(self.spec['bool_options'])):
			(name,opt,value,help) = self.spec['bool_options'][i]
			new = self.booleans[opt].get()
			self.spec['bool_options'][i] = (name,opt,new,help)

		for i in range(len(self.spec['int_options'])):
			(name,opt,value,help) = self.spec['int_options'][i]
			new = self.integers[opt].get()
			self.spec['int_options'][i] = (name,opt,new,help)

		for i in range(len(self.spec['float_options'])):
			(name,opt,value,help) = self.spec['float_options'][i]
			new = self.floats[opt].get()
			self.spec['float_options'][i] = (name,opt,new,help)

		for i in range(len(self.spec['string_options'])):
			(name,opt,value,help) = self.spec['string_options'][i]
			new = self.strings[opt].get()
			self.spec['string_options'][i] = (name,opt,new,help)

		# send the modified options back to the calling window
		self.callback(self.index, self.spec)
		self.master.destroy()

	def cancelWindow(self):
		self.master.destroy()

	def createWidgets(self):
		self.booleans 		= {}
		self.booleanLabels	= {}
		self.booleanInputs	= {}
		self.booleanTT		= {}
		self.integers		= {}
		self.integerLabels	= {}
		self.integerInputs	= {}
		self.integerTT		= {}
		self.floats			= {}
		self.floatLabels	= {}
		self.floatInputs	= {}
		self.floatTT		= {}
		self.strings		= {}
		self.stringLabels	= {}
		self.stringInputs	= {}
		self.stringTT		= {}

		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		rowCounter = 0
		for (name,opt,value,help) in self.spec['bool_options']:
			self.booleans[opt] = tk.IntVar()
			self.booleans[opt].set(value)
			self.booleanLabels[opt] = tk.Label(self.container,text=name)
			self.booleanLabels[opt].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.booleanInputs[opt] = tk.Checkbutton(self.container,variable=self.booleans[opt])
			self.booleanInputs[opt].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			self.booleanTT[opt] = ToolTip(self.booleanLabels[opt],follow_mouse=0,text=help)
			rowCounter+=1

		for (name,opt,value,help) in self.spec['int_options']:
			self.integers[opt] = tk.IntVar()
			self.integers[opt].set(value)
			self.integerLabels[opt] = tk.Label(self.container,text=name)
			self.integerLabels[opt].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.integerInputs[opt] = tk.Entry(self.container,textvariable=self.integers[opt],width=3)
			self.integerInputs[opt].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			self.integerTT[opt] = ToolTip(self.integerLabels[opt],follow_mouse=0,text=help)
			rowCounter+=1

		for (name,opt,value,help) in self.spec['float_options']:
			self.floats[opt] = tk.DoubleVar()
			self.floats[opt].set(value)
			self.floatLabels[opt] = tk.Label(self.container,text=name)
			self.floatLabels[opt].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.floatInputs[opt] = tk.Entry(self.container,textvariable=self.floats[opt],width=4)
			self.floatInputs[opt].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			self.floatTT[opt] = ToolTip(self.floatLabels[opt],follow_mouse=0,text=help)
			rowCounter+=1

		for (name,opt,value,help) in self.spec['string_options']:
			self.strings[opt] = tk.StringVars()
			self.strings[opt].set(value)
			self.stringLabels[opt] = tk.Label(self.container,text=name)
			self.stringLabels[opt].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.stringInputs[opt] = tk.Entry(self.container,textvariable=self.strings[opt],width=4)
			self.stringInputs[opt].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			self.stringTT[opt] = ToolTip(self.stringLabels[opt],follow_mouse=0,text=help)
			rowCounter+=1

		self.cancelButton = tk.Button(self.container,text='Cancel',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,row=rowCounter,sticky=tk.E,pady=8)
		self.saveButton = tk.Button(self.container,text='Save',command=self.saveWindow,default=tk.ACTIVE)
		self.saveButton.grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W,pady=8)
