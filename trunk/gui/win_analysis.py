import Tkinter as tk

class AnalysisWindow(tk.Frame):
	def __init__(self, master, path=None):
		self.master = master

		tk.Frame.__init__(self,master)

		self.grid()
		self.createWidgets()
		
	def createWidgets(self):
		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		self.temp1 = tk.Label(self.container,text='TEST' )
		self.temp1.grid(in_=self.container)
		
	def close(self):
		self.master.destroy()
		