import os
import Tkinter as tk

class LogWindow(tk.Frame):
	def __init__(self, master):
		self.master = master
		self.master.title('MESMER Log')

		tk.Frame.__init__(self,master)

		def ignore():
			# note that a bug in Apple's 10.6 python install prevents this from working as advertised
			# http://bugs.python.org/issue12584
			pass
		self.master.protocol('WM_DELETE_WINDOW',ignore)

		master.columnconfigure(0,weight=1)
		master.rowconfigure(0,weight=1)
		self.grid(column=0,row=0,sticky=tk.N+tk.W+tk.E+tk.S)
		self.columnconfigure(0,weight=1)
		self.rowconfigure(0,weight=1)
		self.createWidgets()

	def cancelWindow(self):
		self.master.destroy()

	def createWidgets(self):

		self.container = tk.Frame(self)
		self.container.grid(in_=self,column=0,row=0,padx=6,pady=6,sticky=tk.N+tk.S+tk.E+tk.W)
		self.container.columnconfigure(0,weight=1)
		self.container.rowconfigure(0,weight=1)

		self.logText = tk.Text(self.container,width=80,height=20)
		self.logText.grid(in_=self.container,column=0,row=0,sticky=tk.N+tk.W+tk.E+tk.S)
		self.logTextScroll = tk.Scrollbar(self.container,orient=tk.VERTICAL)
		self.logTextScroll.grid(in_=self.container,column=1,row=0,sticky=tk.N+tk.W+tk.E+tk.S)
		self.logText.config(yscrollcommand=self.logTextScroll.set)
		self.logTextScroll.config(command=self.logText.yview)

		self.cancelButton = tk.Button(self.container,text='Close',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,columnspan=2,row=1,pady=(8,0))

	def updateLog( self, path ):
		if(self.winfo_exists()):
			rows = int(self.logText.index('end').split('.')[0])-1
			f = open( path )
			for (i,l) in enumerate(f.readlines()):
				if(i>=rows):
					self.logText.insert(tk.END,l)
			f.close()