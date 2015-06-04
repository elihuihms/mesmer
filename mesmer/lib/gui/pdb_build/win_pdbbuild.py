import os
import Tkinter as tk
import tkMessageBox
import tkFileDialog

import mcpdb_objects
import mcpdb_utilities

class PDBBuildWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.title('PDB Builder')

		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=6)
		self.pack_propagate(True)
		
		self.createWidgets()
		self.updateWidgets()

	def loadPDB(self):
		tmp = tkFileDialog.askopenfilename(title='Select PDB coordinate file:',parent=self,filetypes=[('PDB',"*.pdb")])
		if(tmp == ''):
			return

		err,msg = mcpdb_utilities.check_PDB(tmp)
		if err > 0:
			tkMessageBox.showerror("Error",'Problem with PDB file: %s' % (msg),parent=self)
			return
	
		self.pdbChains = mcpdb_utilities.get_chain_info(tmp)
		
		self.pdb = tmp
		self.pdbName.set( os.path.basename(self.pdb) )
		
		lchains = self.pdbChains.keys()
		nchains = len(lchains)
		if nchains == 1:
			self.pdbInfo.set( "1 chain, %i residues"%(self.pdbChains[lchains[0]][1]-self.pdbChains[lchains[0]][0]) )
		else:
			self.pdbInfo.set( "%i chains: %s"%(nchains,",".join(lchains)) )
			
		# remove existing rows
		self.destroyWidgetRows()
			
		self.createWidgetRow()

		self.addRigidGroupButton.config(state=tk.NORMAL)	
	
	def checkGroups(self):
	
		err,msg = mcpdb_utilities.check_groups( self.pdb, groups )
		if err > 0:
			tkMessageBox.showerror("Error",'Problem with group definitions: %s' % (msg),parent=self)
			return False
		
		return True

	def updateWidgets(self, evt=None):
		pass

	def close(self):
		self.master.destroy()

	def createWidgets(self):
		self.pdbLoadButton = tk.Button(self,text='Load PDB...',command=self.loadPDB)
		self.pdbLoadButton.grid(row=0,column=0,sticky=tk.E+tk.W)
		
		self.f_header = tk.LabelFrame(self,text='Info')
		self.f_header.grid(row=1,sticky=tk.E+tk.W)
		self.pdbName = tk.StringVar()
		self.pdbNameLabel = tk.Label(self.f_header,textvariable=self.pdbName)
		self.pdbNameLabel.grid(column=0,row=0,sticky=tk.W)

		self.pdbInfo = tk.StringVar()
		self.pdbInfoLabel = tk.Label(self.f_header,textvariable=self.pdbInfo)
		self.pdbInfoLabel.grid(column=0,row=1,sticky=tk.W)

		self.f_groups = tk.Frame(self)
		self.f_groups.grid(row=2,sticky=tk.E+tk.W)

		self.groupCounter = 0
		self.groupFrames = []
		self.groupLabels = []
		self.groupChainLabels = []
		self.groupChainStarts = []
		self.groupChainStartEntries = []
		self.groupChainEnds = []
		self.groupChainEndEntries = []
		self.groupDeleteButtons = []
		
		self.addRigidGroupButton = tk.Button(self,text='Add Rigid Group',command=lambda: self.createWidgetRow(),state=tk.DISABLED)
		self.addRigidGroupButton.grid(row=3,column=0,sticky=tk.E+tk.W)

		self.f_options = tk.LabelFrame(self,text='Options')
		self.f_options.grid(row=4,sticky=tk.E+tk.W)

		self.fixFirstGroup = tk.IntVar()
		self.fixFirstGroup.set(1)
		self.fixFirstGroupCheckbox = tk.Checkbutton(self.f_options,text='Fix first rigid group',variable=self.fixFirstGroup)
		self.fixFirstGroupCheckbox.grid(row=0,column=0,sticky=tk.W)

		self.useMultiCores = tk.IntVar()
		self.useMultiCores.set(1)
		self.useMultiCoresCheckbox = tk.Checkbutton(self.f_options,text='Use all available CPU cores',variable=self.useMultiCores)
		self.useMultiCoresCheckbox.grid(row=1,column=0,sticky=tk.W)

		self.useRamachandran = tk.IntVar()
		self.useRamachandran.set(0)
		self.useRamachandranCheckbox = tk.Checkbutton(self.f_options,text='Use Ramachandran probabilities',variable=self.useRamachandran,state=tk.DISABLED)
		self.useRamachandranCheckbox.grid(row=2,column=0,sticky=tk.W)

		self.f_footer = tk.Frame(self,borderwidth=0)
		self.f_footer.grid(row=5)

		self.generateButton = tk.Button(self.f_footer,text='Generate PDBs...',default=tk.ACTIVE,command=lambda: makeTargetFromWindow(self),state=tk.DISABLED)
		self.generateButton.grid(column=1,row=6,sticky=tk.W,pady=4)
		self.cancelButton = tk.Button(self.f_footer,text='Cancel',command=self.close)
		self.cancelButton.grid(column=2,row=6,sticky=tk.E,pady=4)

	def createWidgetRow(self):		
		self.groupCounter+=1
		
		self.groupFrames.append( tk.LabelFrame(self.f_groups,text="Rigid Group %i"%(self.groupCounter)) )
		self.groupFrames[-1].grid(row=(self.groupCounter -1)%3,column=int((self.groupCounter-1)/3),ipadx=6,ipady=6)
		
		self.groupLabels.append( [tk.Label(self.groupFrames[-1],text=text) for text in ('Chain:','Start residue:','End residue:')] )
		for i,label in enumerate(self.groupLabels[-1]):
			label.grid(row=i,column=0,sticky=tk.E)
		
		self.groupChainLabels.append( [] )
		self.groupChainStarts.append( [] )
		self.groupChainStartEntries.append( [] )
		self.groupChainEnds.append( [] )
		self.groupChainEndEntries.append( [] )

		for i,chain in enumerate(self.pdbChains):
			self.groupChainLabels[-1].append( tk.Label(self.groupFrames[-1],text=chain ) )
			self.groupChainLabels[-1][-1].grid(column=i+1,row=0)
			
			self.groupChainStarts[-1].append( tk.StringVar() )
			self.groupChainStartEntries[-1].append( tk.Entry(self.groupFrames[-1],width=3,textvariable=self.groupChainStarts[-1][-1]) )
			self.groupChainStartEntries[-1][-1].grid(column=i+1,row=1)
			self.groupChainEnds[-1].append( tk.StringVar() )
			self.groupChainEndEntries[-1].append( tk.Entry(self.groupFrames[-1],width=3,textvariable=self.groupChainEnds[-1][-1]) )
			self.groupChainEndEntries[-1][-1].grid(column=i+1,row=2)

		nchains = len(self.pdbChains)
		self.groupDeleteButtons.append( tk.Button(self.groupFrames[-1],text='Remove Group') )
		self.groupDeleteButtons[-1].grid(column=0,row=3,columnspan=nchains+1,sticky=tk.E+tk.W)
		
#		self.master.geometry('%ix%i' % (max(250,120+nchains*35),320+self.groupCounter*60))
#		self.config(width=max(250,120+nchains*35),height=320+self.groupCounter*60)

	def destroyWidgetRows(self):
		return
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

#		self.master.geometry('720x%i' % (180+self.rowCounter*30))
#		self.config(width=720,height=(180+self.rowCounter*30))