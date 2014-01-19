import os
import Tkinter as tk

from __init__ import __version__

programInfo = {
	'version'	: __version__,
	'author'	: 'Elihu Ihms',
	'copyright'	: """Copyright (C) 2013-2014 Elihu Ihms
This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License version 2 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""
}

class AboutWindow(tk.Frame):
	def __init__(self, master):
		self.master = master
		self.master.geometry('700x480+200+200')
		self.master.resizable(width=False, height=False)
		self.master.title('About MESMER')

		tk.Frame.__init__(self,master)

		self.grid(column=0,row=0,sticky=tk.N+tk.W+tk.E+tk.S)
		self.createWidgets()

	def cancelWindow(self):
		self.master.destroy()

	def createWidgets(self):

		self.container = tk.Frame(self)
		self.container.grid(in_=self,column=0,row=0,padx=6,pady=6,sticky=tk.N+tk.S+tk.E+tk.W)
		self.container.columnconfigure(0,weight=1)
		self.container.rowconfigure(0,weight=1)

		self.f_logo = tk.Frame(self.container)
		self.f_logo.grid(column=0,row=0,pady=(20,0))
		self.LogoImage = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'mesmer_logo.gif'))
		self.LogoLabel = tk.Label(self.f_logo,image=self.LogoImage)
		self.LogoLabel.pack(side=tk.TOP)

		self.aboutText = tk.Label(
			self.container,
			justify='center',
			wraplength=670,
			text="""
MESMER GUI version %s

%s

Special Thanks:

The Mark Foster Lab
The Ohio State Biophysics Program
The Ohio State University
www.shedreamsindigital.net
""" % (programInfo['version'],programInfo['copyright']))

		self.aboutText.grid(in_=self.container,column=0,row=1)

		self.cancelButton = tk.Button(self.container,text='Close',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,columnspan=2,row=2,pady=(8,0))
