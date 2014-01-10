import Tkinter as tk

class StatusWindow(tk.Frame):
	def __init__(self, master, cancelFunc, type=''):
		self.master = master
		self.cancelFunc = cancelFunc
		self.master.resizable(width=False, height=False)
		self.master.title(type)

		tk.Frame.__init__(self,master,width=200,height=100,borderwidth=0)
		self.grid()
		self.grid_propagate(0)

		self.createControlVars()
		self.createWidgets()

	def cancelCalc(self):
		self.cancelFunc()
		self.close()

	def close(self):
		self.master.destroy()

	def createControlVars(self):
		self.CalcProgress	= tk.StringVar()
		self.CalcProgress.set("Progress: 0/0")
		self.CurrentPDB		= tk.StringVar()
		self.CurrentPDB.set("")
		self.AfterID = None

	def createWidgets(self):
		self.container = tk.Frame(self,borderwidth=0)
		self.container.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

		self.CalcProgressLabel = tk.Label(self.container,textvariable=self.CalcProgress)
		self.CalcProgressLabel.grid(in_=self.container,column=0,row=0,sticky=tk.W)

		self.CurrentPDBLabel = tk.Label(self.container,textvariable=self.CurrentPDB)
		self.CurrentPDBLabel.grid(in_=self.container,column=0,row=1,sticky=tk.W)

		self.cancelButton = tk.Button(self.container, text='Cancel',command=self.cancelCalc, width=20)
		self.cancelButton.grid(in_=self.container,column=0,row=2,sticky=tk.E)
