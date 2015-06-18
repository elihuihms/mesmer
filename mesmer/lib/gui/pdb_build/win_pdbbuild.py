import os
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkFont

from multiprocessing import cpu_count,Queue

import mcpdb_objects
import mcpdb_utilities
import mcpdb_generator

_PDB_generator_timer = 500 # in ms
_PDB_generator_format= "%05i.pdb"

class PDBBuildWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.title('PDB Generator')

		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.cancelWindow)

		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=6)
		self.pack_propagate(True)
		
		self.createWidgets()
		
	def cancelWindow(self):
		if self.generatorStatus == 0:
			self.stopPDBGenerators()
			self.master.destroy()
			return

		if tkMessageBox.askquestion("Cancel", "Stop generating structures?", icon='warning',parent=self) == 'yes':
			self.stopPDBGenerators()

	def createWidgets(self):
		self.infoFont = tkFont.Font(slant=tkFont.ITALIC)

		self.pdbLoadButton = tk.Button(self,text='Load PDB...',command=self.loadPDB)
		self.pdbLoadButton.grid(row=0,column=0,sticky=tk.E+tk.W)
		
		self.f_header = tk.LabelFrame(self,text='Info')
		self.f_header.grid(row=1,sticky=tk.E+tk.W)
		self.pdbName = tk.StringVar()
		self.pdbNameLabel = tk.Label(self.f_header,textvariable=self.pdbName,font=self.infoFont)
		self.pdbNameLabel.grid(column=0,row=0,sticky=tk.W)

		self.pdbInfo = tk.StringVar()
		self.pdbInfoLabel = tk.Label(self.f_header,textvariable=self.pdbInfo,font=self.infoFont)
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
		self.groupRemoveButtons = []
		
		self.addRigidGroupButton = tk.Button(self,text='Add Rigid Group',command=lambda: self.createWidgetRow(),state=tk.DISABLED)
		self.addRigidGroupButton.grid(row=3,column=0,sticky=tk.E+tk.W)

		self.f_options = tk.LabelFrame(self,text='Options')
		self.f_options.grid(row=4,sticky=tk.E+tk.W)

		self.pdbPrefix = tk.StringVar()
		self.pdbPrefixLabel = tk.Label(self.f_options,text="Output prefix:")
		self.pdbPrefixLabel.grid(row=0,column=0,sticky=tk.W)
		self.pdbPrefixEntry = tk.Entry(self.f_options,textvariable=self.pdbPrefix)
		self.pdbPrefixEntry.grid(row=0,column=1,sticky=tk.W)
		
		self.pdbNumber = tk.IntVar()
		self.pdbNumber.set( 10 )
		self.pdbNumberLabel = tk.Label(self.f_options,text="Number of PDBs:")
		self.pdbNumberLabel.grid(row=1,column=0,sticky=tk.W)
		self.pdbNumberEntry = tk.Entry(self.f_options,textvariable=self.pdbNumber)
		self.pdbNumberEntry.grid(row=1,column=1,sticky=tk.W)

		self.fixFirstGroup = tk.IntVar()
		self.fixFirstGroup.set(1)
		self.fixFirstGroupCheckbox = tk.Checkbutton(self.f_options,text='Fix first rigid group',variable=self.fixFirstGroup)
		self.fixFirstGroupCheckbox.grid(row=2,column=0,columnspan=2,sticky=tk.W)

		self.useMultiCores = tk.IntVar()
		self.useMultiCores.set(1)
		self.useMultiCoresCheckbox = tk.Checkbutton(self.f_options,text='Use all available CPU cores',variable=self.useMultiCores)
		self.useMultiCoresCheckbox.grid(row=3,column=0,columnspan=2,sticky=tk.W)

		self.useRamachandran = tk.IntVar()
		self.useRamachandran.set(0)
		self.useRamachandranCheckbox = tk.Checkbutton(self.f_options,text='Use Ramachandran linkers',variable=self.useRamachandran)
		self.useRamachandranCheckbox.grid(row=4,column=0,columnspan=2,sticky=tk.W)
		
		self.clashToleranceLabel = tk.Label(self.f_options,text="CA-CA tolerance: ")
		self.clashToleranceLabel.grid(row=5,column=0,sticky=tk.E)
		self.clashTolerance = tk.DoubleVar()
		self.clashTolerance.set(1.0)
		self.clashToleranceEntry = tk.Entry(self.f_options,textvariable=self.clashTolerance,width=3)
		self.clashToleranceEntry.grid(row=5,column=1,sticky=tk.W)

		self.f_footer = tk.Frame(self,borderwidth=0)
		self.f_footer.grid(row=5)

		self.generateButton = tk.Button(self.f_footer,text='Generate PDBs...',default=tk.ACTIVE,command=self.generatePDBs,state=tk.DISABLED)
		self.generateButton.grid(column=1,row=6,sticky=tk.W,pady=4)
		self.cancelButton = tk.Button(self.f_footer,text='Cancel',command=self.cancelWindow)
		self.cancelButton.grid(column=2,row=6,sticky=tk.E,pady=4)
		
		self.generatorStatus = 0

	def createWidgetRow(self,initial=False):		
		self.groupFrames.append( tk.LabelFrame(self.f_groups,text="Rigid Group %i"%(self.groupCounter+1)) )
		self.groupFrames[-1].grid(row=self.groupCounter%3,column=int(self.groupCounter/3),ipadx=6,ipady=6)
		
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
			
			if initial:
				self.groupChainStarts[-1][-1].set( self.pdbChains[chain][0] )
				self.groupChainEnds[-1][-1].set( self.pdbChains[chain][1] )

		nchains = len(self.pdbChains)
		self.groupRemoveButtons.append( tk.Button(self.groupFrames[-1],text='Remove Group') )
		self.groupRemoveButtons[-1].grid(column=0,row=3,columnspan=nchains+1,sticky=tk.E+tk.W)
		self.groupRemoveButtons[-1].bind('<ButtonRelease-1>',self.clearWidgetRow)
		
		self.groupCounter+=1

	def clearWidgetRow(self,event):
		showinfo = True
		for i,button in enumerate(self.groupRemoveButtons):
			if button is event.widget:

				for j,chain in enumerate(self.pdbChains):
					if self.groupChainStarts[i][j].get() != '' or self.groupChainEnds[i][j].get() != '':
						showinfo = False
						
					self.groupChainStarts[i][j].set('')
					self.groupChainEnds[i][j].set('')
					
		if showinfo:
			tkMessageBox.showinfo("Note","Rigid groups without any specified start or end residues are automatically ignored",parent=self)
		
	def destroyWidgetRows(self):
		for i in range(self.groupCounter):
			self.groupFrames[i].destroy()
			
			for j in range(3):
				self.groupLabels[i][j].destroy()
			
			for j in range(len(self.pdbChains)):
				self.groupChainLabels[i][j].destroy()
				self.groupChainStartEntries[i][j].destroy()
				self.groupChainEndEntries[i][j].destroy()

				del self.groupChainStarts[i][j]
				del self.groupChainEnds[i][j]

			self.groupRemoveButtons[i].destroy()
		
		self.groupFrames = []
		self.groupLabels = []
		self.groupChainLabels = []
		self.groupChainStarts = []
		self.groupChainStartEntries = []
		self.groupChainEnds = []
		self.groupChainEndEntries = []
		self.groupRemoveButtons = []

		self.groupCounter = 0
	
	#	
	# action functions
	#
	
	def loadPDB(self):
		tmp = tkFileDialog.askopenfilename(title='Select PDB coordinate file:',parent=self,filetypes=[('PDB',"*.pdb")])
		if(tmp == ''):
			return

		self.destroyWidgetRows()

		self.pdbName.set( "Checking PDB:" )
		self.pdbInfo.set( "Looking for discontinuities..." )
		self.update_idletasks()

		err,msg = mcpdb_utilities.check_PDB(tmp)
		if err > 0:
			tkMessageBox.showerror("Error",'Problem with PDB file: %s' % (msg),parent=self)
			self.pdbName.set( "PDB check failed." )
			self.pdbInfo.set( "" )
			return
	
		self.pdbInfo.set( "Looking for steric clashes..." )
		self.update_idletasks()
		
		model = mcpdb_objects.TransformationModel( tmp, [], 0 )
		clashes = mcpdb_objects.ModelEvaluator( model, clash_radius=self.clashTolerance.get() ).count_clashes()
		if clashes > 0:
			tkMessageBox.showerror("Error","Problem with PDB file: %i CA-CA clashes already exist. Check your PDB's sterics and try again." % (clashes),parent=self)
			self.pdbName.set( "PDB check failed." )
			self.pdbInfo.set( "" )
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
					
		self.createWidgetRow(initial=True)

		self.addRigidGroupButton.config(state=tk.NORMAL)
		self.generateButton.config(state=tk.NORMAL)
	
	def generatePDBs(self):	
		groups = []
		for i in xrange(self.groupCounter):
			groups.append( [] )
			
			for j,chain in enumerate(self.pdbChains):
				if self.groupChainStarts[i][j].get() != '' and self.groupChainEnds[i][j].get() != '':
					start	= int(self.groupChainStarts[i][j].get())
					end		= int(self.groupChainEnds[i][j].get())
					groups[-1].append( (chain,start,end) )
			
			if groups[-1] == []:
				groups.pop( len(groups) -1 )
			
		err,msg = mcpdb_utilities.check_groups( self.pdb, groups )
		if err > 0:
			tkMessageBox.showerror("Error",'Problem with group definitions: %s' % (msg),parent=self)
			return
		
		dir = tkFileDialog.askdirectory(title="Choose a directory to save generated PDBs into:",parent=self)
		if dir == '':
			return
		
		prefix = self.pdbPrefix.get()
		show_warning = True
		
		self.pdbInfo.set( "Scanning existing directory..." )
		self.update_idletasks()
	
		self.in_Queue,self.out_Queue = Queue(),Queue()
		for i in range(self.pdbNumber.get()):
			if os.path.exists(os.path.join(dir,prefix+(_PDB_generator_format%(i)))):
			
				if show_warning:
					if tkMessageBox.askquestion("Warning", "Directory already contains PDBs, PDB generator will start where previous iterations left off.", icon='warning', parent=self) != 'yes':
						return
					show_warning = False
					
			else:
				self.in_Queue.put( i )
				
		self.pdbName.set( "Generating PDBs:" )
		self.pdbInfo.set( "Initializing generators..." )
		self.update_idletasks()
		
		if self.useMultiCores.get() > 0:
			self.pdbGenerators = [None]*cpu_count()
		else:
			self.pdbGenerators = [None]
		
		for i in xrange(len(self.pdbGenerators)):
			self.pdbGenerators[i] = mcpdb_generator.PDBGenerator(
				self.in_Queue,
				self.out_Queue,
				self.pdb,
				groups,
				use_rama=(self.useRamachandran.get() == 1),
				fix_first=(self.fixFirstGroup.get() == 1),
				dir=dir,
				prefix=prefix,
				format=_PDB_generator_format,
				eval_kwargs={'clash_radius':self.clashTolerance.get()},
				seed=i*100
			)
			self.pdbGenerators[i].start()
		
		self.pdbInfo.set( "Generating structures..." )
		self.update_idletasks()
		self.generatorStatus = 1
		self.after( _PDB_generator_timer, self.updatePDBGenerators )

	def updatePDBGenerators(self):
		# get all of the indices generated since the last call
		indices = []
		while not self.out_Queue.empty():
			indices.append( self.out_Queue.get() )
		indices.sort(reverse=True)
		
		if len(indices) > 0:
			self.pdbInfo.set( "Generated structure %i of %i"%(indices[0]+1,self.pdbNumber.get()) )
		
			if indices[0]+1 == self.pdbNumber.get():
				self.stopPDBGenerators()
				return
					
		self.after( _PDB_generator_timer, self.updatePDBGenerators )
	
	def stopPDBGenerators(self):
		# send term signal to workers
		for i in xrange(len(self.pdbGenerators)):
			self.in_Queue.put( None )
		
		self.pdbInfo.set( "Stopping generators..." )
		self.update_idletasks()
			
		# make sure they're all shut down
		for i in xrange(len(self.pdbGenerators)):
			if self.pdbGenerators[i] != None:
				self.pdbGenerators[i].join()
			self.pdbGenerators[i] = None
			
		self.pdbIndices = []
		self.pdbName.set( "Done." )
		self.pdbInfo.set( "" )
		self.update_idletasks()
		self.generatorStatus = 0