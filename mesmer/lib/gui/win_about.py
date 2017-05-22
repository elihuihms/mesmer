import os
import Tkinter as tk
import codecs

from __init__ import __version__
from .. __init__ import __copyright__

__acknowledgements__ = codecs.decode("""Fcrpvny gunaxf gb:

Revp Qnauneg
Znex Sbfgre
Naa Vuzf
Unaanu Vuzf
Anguna Wbarf
Eboregb Fnyvanf
Naan Fzvgu
Ncnean Haavxevfuana
Ivouhgv Jnqujn
Yv Munat
Rhtrar Inyxbi
Gbzbuvqr Fnvb

Gur BFH Ovbculfvpf Ngbzvp Erfbyhgvba fznyy tebhc
Gur FVOLYF fgnss ng YOAY
 
jjj.furqernzfvaqvtvgny.arg""",'rot_13')

class AboutWindow(tk.Frame):
	def __init__(self, master):
		self.master = master
		self.master.title('About MESMER')
		self.master.resizable(width=False, height=False)
		
		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=0)
		self.pack_propagate(True)

		self.createWidgets()

	def close(self):
		self.master.destroy()
		
	def scrolltext(self):
		if self.scrollcounter > 300:
			self.scrollcounter = -100
			self.aboutCanvas.yview_scroll(-400,tk.UNITS)
			
		self.aboutCanvas.yview_scroll(1,tk.UNITS)
		self.after(50, self.scrolltext)
		self.scrollcounter+=1
		
	def createWidgets(self):

		self.container = tk.Frame(self)
		self.container.grid(column=0,row=0,padx=6,pady=6,sticky=tk.N+tk.S+tk.E+tk.W)
		self.container.columnconfigure(0,weight=1)
		self.container.rowconfigure(0,weight=1)

		self.f_logo = tk.Frame(self.container)
		self.f_logo.grid(column=0,row=0,pady=(20,0))
		self.LogoImage = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'mesmer_logo.gif'))
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.TOP)

		self.infoText = tk.Label(
			self.container,
			justify='center',
			wraplength=670,
			text="MESMER GUI version %s\n\n%s"%(__version__,__copyright__))
		self.infoText.grid(column=0,row=1)

		self.aboutCanvas = tk.Canvas(self.container,width=400,height=100,borderwidth=2)
		self.aboutCanvas.grid(column=0,row=2)
		self.aboutCanvas.create_text(200,10,anchor="n",justify='center',text=__acknowledgements__)
		self.aboutCanvas.configure(yscrollincrement='1')
		self.scrollcounter = 0
		self.after(1000, self.scrolltext)

#		self.cancelButton = tk.Button(self.container,text='Close',command=self.close)
#		self.cancelButton.grid(column=0,columnspan=2,row=3,pady=(8,0))
		
