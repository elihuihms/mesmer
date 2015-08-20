import os
import glob
import tempfile

import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkFont

from ... setup_functions import open_user_prefs
from .. tools_multiprocessing import FunctionParallelizer
from .. tools_TkTooltip import ToolTip
from tools_pdbattr import *

import tools_rmsd
import tools_geom

_PDB_calculator_timer = 500 # in ms, time between updating the calculation status text

class PDBAttributeWindow(tk.Frame):
	"""Window for calculating attributes from a library of PDBs
	Can either create a new tab-delimited attribute table, or append to an existing one"""
	
	def __init__(self, master=None):
		self.master = master
		self.master.title('PDB Attribute Calculator')

		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=6)
		self.pack_propagate(True)
		
		self.createWidgets()
		self.pdbList = []
		self.Calculator = None
	
		try:
			self.prefs = open_user_prefs(mode='r')
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()
							
	def close(self):
		"""Stop any calculations if they are running, and close the window"""
		if self.Calculator == None:
			self.master.destroy()
			return
		elif tkMessageBox.askquestion("Cancel", "Stop calculations? Progress will be lost.", icon='warning',parent=self) == 'yes':
			self.stopCalculator(abort=True)
			return

	def createWidgets(self):
		"""Fill the window with widgets"""
		self.infoFont = tkFont.Font(slant=tkFont.ITALIC)
	
		self.pdb_frame = tk.LabelFrame(self,text='PDB Directory')
		self.pdb_frame.grid(row=0,sticky=tk.E+tk.W)		
		self.pdb_frame.grid_columnconfigure(1,weight=1)
		self.pdbDirectoryPath = tk.StringVar()
		self.pdbDirectoryEntry = tk.Entry(self.pdb_frame,textvariable=self.pdbDirectoryPath,width=25)
		self.pdbDirectoryEntry.grid(row=0,column=0,sticky=tk.W)
		self.pdbDirectoryButton = tk.Button(self.pdb_frame,text='Set...',command=self.loadDirPDBs)
		self.pdbDirectoryButton.grid(row=0,column=1,sticky=tk.W)
		self.pdbDirectoryButtonTT = ToolTip(self.pdbDirectoryButton,follow_mouse=0,text='Set a directory containing PDBs to calculate attributes from.')
		self.pdbDirectoryInfo = tk.Label(self.pdb_frame,text='Idle - No PDBs loaded.',font=self.infoFont)
		self.pdbDirectoryInfo.grid(row=1,columnspan=2,sticky=tk.W)
		
		self.button_frame = tk.LabelFrame(self,text="Attribute to calculate")
		self.button_frame.grid(row=1,sticky=tk.E+tk.W)
		self.calc_RMSD_Button = tk.Button(self.button_frame,text="RMSD",default=tk.ACTIVE)
		self.calc_RMSD_Button.grid(row=0,column=0)
		self.calc_RMSD_Button.bind('<ButtonRelease-1>',self.setActionPane)
		self.calc_RMSD_ButtonTT = ToolTip(self.calc_RMSD_Button,follow_mouse=0,text='Calculate the RMSD against a reference PDB for the selected PDBs.')
		self.calc_Rg_Button = tk.Button(self.button_frame,text="Rg")
		self.calc_Rg_Button.grid(row=0,column=1)
		self.calc_Rg_Button.bind('<ButtonRelease-1>',self.setActionPane)
		self.calc_Rg_ButtonTT = ToolTip(self.calc_Rg_Button,follow_mouse=0,text='Calculate the radius of gyration for the selected PDBs.')
		self.calc_Distance_Button = tk.Button(self.button_frame,text="Distance")
		self.calc_Distance_Button.grid(row=0,column=2)
		self.calc_Distance_Button.bind('<ButtonRelease-1>',self.setActionPane)
		self.calc_Distance_ButtonTT = ToolTip(self.calc_Distance_Button,follow_mouse=0,text='Calculate the distance between two atoms for the selected PDBs.')
		self.calc_Angle_Button = tk.Button(self.button_frame,text="Angle")
		self.calc_Angle_Button.grid(row=0,column=3)
		self.calc_Angle_Button.bind('<ButtonRelease-1>',self.setActionPane)
		self.calc_Angle_ButtonTT = ToolTip(self.calc_Angle_Button,follow_mouse=0,text='Calculate the angle between three atoms in the selected PDBs.')
		self.calc_Dihedral_Button = tk.Button(self.button_frame,text="Dihedral")
		self.calc_Dihedral_Button.grid(row=0,column=4)
		self.calc_Dihedral_Button.bind('<ButtonRelease-1>',self.setActionPane)
		self.calc_Dihedral_ButtonTT = ToolTip(self.calc_Dihedral_Button,follow_mouse=0,text='Calculate the dihedral angle between four atoms in the selected PDBs.')
	
		self.calc_RMSD_frame = tk.Frame(self.button_frame)
		self.calc_RMSD_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
		self.calc_RMSD_frame.grid_columnconfigure(1,weight=1)
		self.fillRMSDFrame()
		self.calc_Rg_frame = tk.Frame(self.button_frame)
		self.fillRgFrame()
		self.calc_Distance_frame = tk.Frame(self.button_frame)
		self.fillDistanceFrame()
		self.calc_Angle_frame = tk.Frame(self.button_frame)
		self.fillAngleFrame()
		self.calc_Dihedral_frame = tk.Frame(self.button_frame)
		self.fillDihedralFrame()

		self.attr_frame = tk.LabelFrame(self,text='Attribute Table')
		self.attr_frame.grid(row=2,sticky=tk.E+tk.W)
		self.attr_frame.grid_columnconfigure(2,weight=1)
		self.attr_frame.grid_columnconfigure(3,weight=1)
		self.attributeFilePath = tk.StringVar()
		self.attributeFileEntry = tk.Entry(self.attr_frame,textvariable=self.attributeFilePath,width=25)
		self.attributeFileEntry.grid(row=0,column=0,columnspan=2,sticky=tk.W)
		self.attributeFileSetButton = tk.Button(self.attr_frame,text='Set...',command=lambda: self.setAttributeTable(new=False),state=tk.DISABLED)
		self.attributeFileSetButton.grid(row=0,column=2,sticky=tk.W)
		self.attributeFileSetButtonTT = ToolTip(self.attributeFileSetButton,follow_mouse=0,text='Write or append attributes to an existing attribute table.')
		self.attributeFileNewButton = tk.Button(self.attr_frame,text='New...',command=lambda: self.setAttributeTable(new=True),state=tk.DISABLED)
		self.attributeFileNewButton.grid(row=0,column=3,sticky=tk.W)
		self.attributeFileNewButtonTT = ToolTip(self.attributeFileNewButton,follow_mouse=0,text='Create a new attribute table from the selected PDBs.')
		self.attributeFileInfo = tk.Label(self.attr_frame,text='Idle - No attribute list loaded.',font=self.infoFont)
		self.attributeFileInfo.grid(row=1,columnspan=4,sticky=tk.W)
		self.attributeFileColLabel = tk.Label(self.attr_frame,text="Save to column:")
		self.attributeFileColLabel.grid(row=2,column=0,columnspan=2,sticky=tk.W)
		self.attributeFileColSel	= tk.StringVar()
		options = ('none')
		self.attributeFileColMenu = tk.OptionMenu(self.attr_frame,self.attributeFileColSel,*options)
		self.attributeFileColMenu.grid(row=2,column=1,columnspan=3,sticky=tk.W)
		self.attributeFileColMenu.config(state=tk.DISABLED,width=25)
		self.attributeFileColMenuTT = ToolTip(self.attributeFileColMenu,follow_mouse=0,text='Select an existing column or append a new column to the selected attribute table.')

		self.f_footer = tk.Frame(self)
		self.f_footer.grid(row=4,sticky=tk.E+tk.W)
		self.calculateButton = tk.Button(self.f_footer,text='Calculate...',state=tk.DISABLED,command=self.startCalculator)
		self.calculateButton.grid(column=0,row=0,sticky=tk.E,pady=4)
		self.calculateButtonTT = ToolTip(self.calculateButton,follow_mouse=0,text='Start calculating the selected attribute from the loaded PDBs.')
		self.cancelButton = tk.Button(self.f_footer,text='Close',command=self.close)
		self.cancelButton.grid(column=1,row=0,sticky=tk.E,pady=4)
		self.cancelButtonTT = ToolTip(self.cancelButton,follow_mouse=0,text='Cancel any existing calculations in progress, and close the window.')

	def setActionPane(self,evt):
		"""Set the attribute calculation pane based upon which attribute button was pressed
		
		Args:
			evt	(Tkinter event): Contains the pressed button
			
		Returns: None"""
		self.calc_RMSD_Button.configure(default=tk.NORMAL)
		self.calc_Rg_Button.configure(default=tk.NORMAL)
		self.calc_Distance_Button.configure(default=tk.NORMAL)
		self.calc_Angle_Button.configure(default=tk.NORMAL)
		self.calc_Dihedral_Button.configure(default=tk.NORMAL)
		evt.widget.configure(default=tk.ACTIVE)

		self.calc_RMSD_frame.grid_forget()
		self.calc_Rg_frame.grid_forget()
		self.calc_Distance_frame.grid_forget()
		self.calc_Angle_frame.grid_forget()
		self.calc_Dihedral_frame.grid_forget()
				
		if evt.widget == self.calc_RMSD_Button:
			self.calc_RMSD_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
		elif evt.widget == self.calc_Rg_Button:
			self.calc_Rg_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
		elif evt.widget == self.calc_Distance_Button:
			self.calc_Distance_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
		elif evt.widget == self.calc_Angle_Button:
			self.calc_Angle_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
		elif evt.widget == self.calc_Dihedral_Button:
			self.calc_Dihedral_frame.grid(row=1,columnspan=5,sticky=tk.E+tk.W)
			
		self.updateCalculateButton()

	def fillRMSDFrame(self):
		"""Fill the RMSD attribute calculation frame with widgets"""
		self.calc_RMSD_Label = tk.Label(self.calc_RMSD_frame,text="Reference PDB:")
		self.calc_RMSD_Label.grid(row=0,columnspan=2,sticky=tk.W)
		self.calc_RMSD_PDBPath = tk.StringVar()
		self.calc_RMSD_PDBEntry = tk.Entry(self.calc_RMSD_frame,textvariable=self.calc_RMSD_PDBPath,width=25)
		self.calc_RMSD_PDBEntry.grid(row=1,column=0,sticky=tk.W)
		self.calc_RMSD_PDBButton = tk.Button(self.calc_RMSD_frame,text="Set...",command=self.setRMSDReference)
		self.calc_RMSD_PDBButton.grid(row=1,column=1,sticky=tk.W)
		self.calc_RMSD_PDBButtonTT = ToolTip(self.calc_RMSD_PDBButton,follow_mouse=0,text='Set the reference PDB to calculate RMSD values against.')
		
		self.calc_RMSD_SuperimposeSelFrame = tk.LabelFrame(self.calc_RMSD_frame,text="Residues to superimpose:")
		self.calc_RMSD_SuperimposeSelFrame.grid(row=2,columnspan=2,sticky=tk.E+tk.W,padx=10,pady=5)
		self.calc_RMSD_SuperimposeSelFrame.grid_columnconfigure(1,weight=1)

		self.calc_RMSD_SuperimposeSel = tk.IntVar()
		self.calc_RMSD_SuperimposeSel.set(0)
		self.calc_RMSD_SuperimposeRadioFrame = tk.Frame(self.calc_RMSD_SuperimposeSelFrame)
		self.calc_RMSD_SuperimposeRadioFrame.grid(columnspan=2,sticky=tk.W)
		self.calc_RMSD_SuperimposeRadio0 = tk.Radiobutton(self.calc_RMSD_SuperimposeRadioFrame, variable=self.calc_RMSD_SuperimposeSel, text="All residues", value=0, command=self.set_RMSD_SuperimposeSel)
		self.calc_RMSD_SuperimposeRadio0.grid(row=0,column=0,sticky=tk.W)
		self.calc_RMSD_SuperimposeRadio0TT = ToolTip(self.calc_RMSD_SuperimposeRadio0,follow_mouse=0,text='Try to superimpose all residues in the reference and each of the selected PDBs.')
		self.calc_RMSD_SuperimposeRadio1 = tk.Radiobutton(self.calc_RMSD_SuperimposeRadioFrame, variable=self.calc_RMSD_SuperimposeSel, text="Some residues", value=1, command=self.set_RMSD_SuperimposeSel)
		self.calc_RMSD_SuperimposeRadio1.grid(row=0,column=1,sticky=tk.W)
		self.calc_RMSD_SuperimposeRadio1TT = ToolTip(self.calc_RMSD_SuperimposeRadio1,follow_mouse=0,text='Try to superimpose a selected subset of residues in the reference and each of the selected PDBs.')
		self.calc_RMSD_SuperimposeRadio2 = tk.Radiobutton(self.calc_RMSD_SuperimposeRadioFrame, variable=self.calc_RMSD_SuperimposeSel, text="No residues", value=2, command=self.set_RMSD_SuperimposeSel)
		self.calc_RMSD_SuperimposeRadio2.grid(row=0,column=2,sticky=tk.W)
		self.calc_RMSD_SuperimposeRadio2TT = ToolTip(self.calc_RMSD_SuperimposeRadio2,follow_mouse=0,text='Do not try and superimpose the reference and each of the selected PDBs before calculating RMSD.')
	
		self.calc_RMSD_SuperimposeChainLabel = tk.Label(self.calc_RMSD_SuperimposeSelFrame,text="Chain:")
		self.calc_RMSD_SuperimposeResStartLabel = tk.Label(self.calc_RMSD_SuperimposeSelFrame,text="Starting residue:")
		self.calc_RMSD_SuperimposeResEndLabel = tk.Label(self.calc_RMSD_SuperimposeSelFrame,text="Ending residue:")
		self.calc_RMSD_SuperimposeChain = tk.StringVar()
		self.calc_RMSD_SuperimposeChainEntry = tk.Entry(self.calc_RMSD_SuperimposeSelFrame,textvariable=self.calc_RMSD_SuperimposeChain,width=2)
		self.calc_RMSD_SuperimposeResStart = tk.IntVar()
		self.calc_RMSD_SuperimposeResStartEntry = tk.Entry(self.calc_RMSD_SuperimposeSelFrame,textvariable=self.calc_RMSD_SuperimposeResStart,width=4)
		self.calc_RMSD_SuperimposeResEnd = tk.IntVar()
		self.calc_RMSD_SuperimposeResEndEntry = tk.Entry(self.calc_RMSD_SuperimposeSelFrame,textvariable=self.calc_RMSD_SuperimposeResEnd,width=4)
				
		self.calc_RMSD_CalcSelFrame = tk.LabelFrame(self.calc_RMSD_frame,text="Calculate RMSD between:")
		self.calc_RMSD_CalcSelFrame.grid(row=3,columnspan=2,sticky=tk.E+tk.W,padx=10,pady=5)
		self.calc_RMSD_CalcSelFrame.grid_columnconfigure(1,weight=1)

		self.calc_RMSD_CalcSel = tk.IntVar()
		self.calc_RMSD_CalcSel.set(0)
		self.calc_RMSD_CalcRadioFrame = tk.Frame(self.calc_RMSD_CalcSelFrame)
		self.calc_RMSD_CalcRadioFrame.grid(columnspan=2,sticky=tk.W)
		self.calc_RMSD_CalcRadio0 = tk.Radiobutton(self.calc_RMSD_CalcRadioFrame, variable=self.calc_RMSD_CalcSel, text="All residues", value=0, command=self.set_RMSD_CalcSel)
		self.calc_RMSD_CalcRadio0.grid(row=0,column=0,sticky=tk.W)
		self.calc_RMSD_CalcRadio0TT = ToolTip(self.calc_RMSD_CalcRadio0,follow_mouse=0,text='Use all residues in the reference and selected PDBs for the RMSD calculation.')
		self.calc_RMSD_CalcRadio1 = tk.Radiobutton(self.calc_RMSD_CalcRadioFrame, variable=self.calc_RMSD_CalcSel, text="Some residues", value=1, command=self.set_RMSD_CalcSel)
		self.calc_RMSD_CalcRadio1.grid(row=0,column=1,sticky=tk.W)
		self.calc_RMSD_CalcRadio1TT = ToolTip(self.calc_RMSD_CalcRadio1,follow_mouse=0,text='Use a subset of residues in the reference and selected PDBs for the RMSD calculation.')
		
		self.calc_RMSD_CalcChainLabel = tk.Label(self.calc_RMSD_CalcSelFrame,text="Chain:")
		self.calc_RMSD_CalcChain = tk.StringVar()
		self.calc_RMSD_CalcChainEntry = tk.Entry(self.calc_RMSD_CalcSelFrame,textvariable=self.calc_RMSD_CalcChain,width=2)
		self.calc_RMSD_CalcResStartLabel = tk.Label(self.calc_RMSD_CalcSelFrame,text="Starting residue:")
		self.calc_RMSD_CalcResStart = tk.IntVar()
		self.calc_RMSD_CalcResStartEntry = tk.Entry(self.calc_RMSD_CalcSelFrame,textvariable=self.calc_RMSD_CalcResStart,width=4)
		self.calc_RMSD_CalcResEndLabel = tk.Label(self.calc_RMSD_CalcSelFrame,text="Ending residue:")
		self.calc_RMSD_CalcResEnd = tk.IntVar()
		self.calc_RMSD_CalcResEndEntry = tk.Entry(self.calc_RMSD_CalcSelFrame,textvariable=self.calc_RMSD_CalcResEnd,width=4)

	def set_RMSD_SuperimposeSel(self):
		"""Set which widgets are shown in frame specifying which atoms to use in the RMSD superimposition"""
		if self.calc_RMSD_SuperimposeSel.get() == 1:
			self.calc_RMSD_SuperimposeChainLabel.grid(row=1,column=0,sticky=tk.E)
			self.calc_RMSD_SuperimposeResStartLabel.grid(row=2,column=0,sticky=tk.E)
			self.calc_RMSD_SuperimposeResEndLabel.grid(row=3,column=0,sticky=tk.E)
			self.calc_RMSD_SuperimposeChainEntry.grid(row=1,column=1,sticky=tk.W)
			self.calc_RMSD_SuperimposeResStartEntry.grid(row=2,column=1,sticky=tk.W)
			self.calc_RMSD_SuperimposeResEndEntry.grid(row=3,column=1,sticky=tk.W)
		else:
			self.calc_RMSD_SuperimposeChainLabel.grid_forget()
			self.calc_RMSD_SuperimposeResStartLabel.grid_forget()
			self.calc_RMSD_SuperimposeResEndLabel.grid_forget()
			self.calc_RMSD_SuperimposeChainEntry.grid_forget()
			self.calc_RMSD_SuperimposeResStartEntry.grid_forget()
			self.calc_RMSD_SuperimposeResEndEntry.grid_forget()
	
	def set_RMSD_CalcSel(self):
		"""Set which widgets are shown in the frame specifying which atoms to use in the RMSD calculation"""
		if self.calc_RMSD_CalcSel.get() == 1:
			self.calc_RMSD_CalcChainLabel.grid(row=1,column=0,sticky=tk.E)
			self.calc_RMSD_CalcResStartLabel.grid(row=2,column=0,sticky=tk.E)
			self.calc_RMSD_CalcResEndLabel.grid(row=3,column=0,sticky=tk.E)
			self.calc_RMSD_CalcChainEntry.grid(row=1,column=1,sticky=tk.W)
			self.calc_RMSD_CalcResStartEntry.grid(row=2,column=1,sticky=tk.W)
			self.calc_RMSD_CalcResEndEntry.grid(row=3,column=1,sticky=tk.W)
		else:
			self.calc_RMSD_CalcChainLabel.grid_forget()
			self.calc_RMSD_CalcResStartLabel.grid_forget()
			self.calc_RMSD_CalcResEndLabel.grid_forget()
			self.calc_RMSD_CalcChainEntry.grid_forget()
			self.calc_RMSD_CalcResStartEntry.grid_forget()
			self.calc_RMSD_CalcResEndEntry.grid_forget()
			
	def fillRgFrame(self):
		"""Fill the Rg calculation frame with widgets"""
		self.calc_Rg_AtomSel = tk.IntVar()
		self.calc_Rg_AtomSel.set(0)
		self.calc_Rg_AtomSelRadio0 = tk.Radiobutton(self.calc_Rg_frame, variable=self.calc_Rg_AtomSel, text="Only CA atoms", value=0)
		self.calc_Rg_AtomSelRadio0.grid(row=0,column=0,sticky=tk.W)
		self.calc_Rg_AtomSelRadio0TT = ToolTip(self.calc_Rg_AtomSelRadio0,follow_mouse=0,text='Use only the CA atoms to calculate Rg, which is somewhat faster than using all atoms, especially for large proteins/complexes.')
		self.calc_Rg_AtomSelRadio1 = tk.Radiobutton(self.calc_Rg_frame, variable=self.calc_Rg_AtomSel, text="All atoms", value=1)
		self.calc_Rg_AtomSelRadio1.grid(row=0,column=1,sticky=tk.W)
		self.calc_Rg_AtomSelRadio1TT = ToolTip(self.calc_Rg_AtomSelRadio1,follow_mouse=0,text='Use all the atoms in the PDB to calculate Rg, which can be somewhat slow, especially for large proteins/complexes.')
		
	def fillDistanceFrame(self):
		"""Fill the distance calculation frame with widgets"""
		self.calc_Distance_Chain_Label = tk.Label(self.calc_Distance_frame,text="Chain:")
		self.calc_Distance_Chain_Label.grid(row=1,column=0,sticky=tk.E)
		self.calc_Distance_Res_Label = tk.Label(self.calc_Distance_frame,text="Residue:")
		self.calc_Distance_Res_Label.grid(row=2,column=0,sticky=tk.E)
		self.calc_Distance_Atom_Label = tk.Label(self.calc_Distance_frame,text="Name:")
		self.calc_Distance_Atom_Label.grid(row=3,column=0,sticky=tk.E)
		self.calc_Distance_Label_A = tk.Label(self.calc_Distance_frame,text='Atom 1',fg='red')
		self.calc_Distance_Label_A.grid(row=0,column=1,sticky=tk.E+tk.W)
		self.calc_Distance_Label_B = tk.Label(self.calc_Distance_frame,text='Atom 2',fg='blue')
		self.calc_Distance_Label_B.grid(row=0,column=2,sticky=tk.E+tk.W)
	
		self.calc_Distance_SelA_Chain = tk.StringVar()
		self.calc_Distance_SelA_Res = tk.IntVar()
		self.calc_Distance_SelA_Atom = tk.StringVar()
		self.calc_Distance_SelA_Atom.set('CA')
		self.calc_Distance_SelB_Chain = tk.StringVar()
		self.calc_Distance_SelB_Res = tk.IntVar()
		self.calc_Distance_SelB_Atom = tk.StringVar()
		self.calc_Distance_SelB_Atom.set('CA')

		self.calc_Distance_SelA_Chain_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelA_Chain,width=2)
		self.calc_Distance_SelA_Chain_Entry.grid(row=1,column=1,sticky=tk.W)
		self.calc_Distance_SelA_Res_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelA_Res,width=4)
		self.calc_Distance_SelA_Res_Entry.grid(row=2,column=1,sticky=tk.W)
		self.calc_Distance_SelA_Atom_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelA_Atom,width=3)
		self.calc_Distance_SelA_Atom_Entry.grid(row=3,column=1,sticky=tk.W)
		self.calc_Distance_SelB_Chain_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelB_Chain,width=2)
		self.calc_Distance_SelB_Chain_Entry.grid(row=1,column=2,sticky=tk.W)
		self.calc_Distance_SelB_Res_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelB_Res,width=4)
		self.calc_Distance_SelB_Res_Entry.grid(row=2,column=2,sticky=tk.W)
		self.calc_Distance_SelB_Atom_Entry = tk.Entry(self.calc_Distance_frame,textvariable=self.calc_Distance_SelB_Atom,width=3)
		self.calc_Distance_SelB_Atom_Entry.grid(row=3,column=2,sticky=tk.W)
		
		self.calc_Distance_image = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'image_distance.gif'))
		self.calc_Distance_imageLabel = tk.Label(self.calc_Distance_frame,image=self.calc_Distance_image)
		self.calc_Distance_frame.grid_columnconfigure(3,weight=1)
		self.calc_Distance_imageLabel.grid(row=1,column=3,rowspan=3,sticky=tk.E,padx=5)

	def fillAngleFrame(self):
		"""Fill the angle calculation frame with widgets"""
		self.calc_Angle_Chain_Label = tk.Label(self.calc_Angle_frame,text="Chain:")
		self.calc_Angle_Chain_Label.grid(row=1,column=0,sticky=tk.E)
		self.calc_Angle_Res_Label = tk.Label(self.calc_Angle_frame,text="Residue:")
		self.calc_Angle_Res_Label.grid(row=2,column=0,sticky=tk.E)
		self.calc_Angle_Atom_Label = tk.Label(self.calc_Angle_frame,text="Name:")
		self.calc_Angle_Atom_Label.grid(row=3,column=0,sticky=tk.E)
		self.calc_Angle_Label_A = tk.Label(self.calc_Angle_frame,text='Atom 1',fg='red')
		self.calc_Angle_Label_A.grid(row=0,column=1,sticky=tk.E+tk.W)
		self.calc_Angle_Label_B = tk.Label(self.calc_Angle_frame,text='Atom 2',fg='blue')
		self.calc_Angle_Label_B.grid(row=0,column=2,sticky=tk.E+tk.W)
		self.calc_Angle_Label_C = tk.Label(self.calc_Angle_frame,text='Atom 3',fg='green3')
		self.calc_Angle_Label_C.grid(row=0,column=3,sticky=tk.E+tk.W)
	
		self.calc_Angle_SelA_Chain = tk.StringVar()
		self.calc_Angle_SelA_Res = tk.IntVar()
		self.calc_Angle_SelA_Atom = tk.StringVar()
		self.calc_Angle_SelA_Atom.set('CA')
		self.calc_Angle_SelB_Chain = tk.StringVar()
		self.calc_Angle_SelB_Res = tk.IntVar()
		self.calc_Angle_SelB_Atom = tk.StringVar()
		self.calc_Angle_SelB_Atom.set('CA')
		self.calc_Angle_SelC_Chain = tk.StringVar()
		self.calc_Angle_SelC_Res = tk.IntVar()
		self.calc_Angle_SelC_Atom = tk.StringVar()
		self.calc_Angle_SelC_Atom.set('CA')

		self.calc_Angle_SelA_Chain_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelA_Chain,width=2)
		self.calc_Angle_SelA_Chain_Entry.grid(row=1,column=1,sticky=tk.W)
		self.calc_Angle_SelA_Res_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelA_Res,width=4)
		self.calc_Angle_SelA_Res_Entry.grid(row=2,column=1,sticky=tk.W)
		self.calc_Angle_SelA_Atom_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelA_Atom,width=3)
		self.calc_Angle_SelA_Atom_Entry.grid(row=3,column=1,sticky=tk.W)
		self.calc_Angle_SelB_Chain_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelB_Chain,width=2)
		self.calc_Angle_SelB_Chain_Entry.grid(row=1,column=2,sticky=tk.W)
		self.calc_Angle_SelB_Res_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelB_Res,width=4)
		self.calc_Angle_SelB_Res_Entry.grid(row=2,column=2,sticky=tk.W)
		self.calc_Angle_SelB_Atom_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelB_Atom,width=3)
		self.calc_Angle_SelB_Atom_Entry.grid(row=3,column=2,sticky=tk.W)
		self.calc_Angle_SelC_Chain_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelC_Chain,width=2)
		self.calc_Angle_SelC_Chain_Entry.grid(row=1,column=3,sticky=tk.W)
		self.calc_Angle_SelC_Res_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelC_Res,width=4)
		self.calc_Angle_SelC_Res_Entry.grid(row=2,column=3,sticky=tk.W)
		self.calc_Angle_SelC_Atom_Entry = tk.Entry(self.calc_Angle_frame,textvariable=self.calc_Angle_SelC_Atom,width=3)
		self.calc_Angle_SelC_Atom_Entry.grid(row=3,column=3,sticky=tk.W)
		
		self.calc_Angle_image = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'image_angle.gif'))
		self.calc_Angle_imageLabel = tk.Label(self.calc_Angle_frame,image=self.calc_Angle_image)
		self.calc_Angle_frame.grid_columnconfigure(4,weight=1)
		self.calc_Angle_imageLabel.grid(row=1,column=4,rowspan=3,sticky=tk.E,padx=5)
		
	def fillDihedralFrame(self):
		"""Fill the dihedral calculation frame with widgets"""
		self.calc_Dihedral_Chain_Label = tk.Label(self.calc_Dihedral_frame,text="Chain:")
		self.calc_Dihedral_Chain_Label.grid(row=1,column=0,sticky=tk.E)
		self.calc_Dihedral_Res_Label = tk.Label(self.calc_Dihedral_frame,text="Residue:")
		self.calc_Dihedral_Res_Label.grid(row=2,column=0,sticky=tk.E)
		self.calc_Dihedral_Atom_Label = tk.Label(self.calc_Dihedral_frame,text="Name:")
		self.calc_Dihedral_Atom_Label.grid(row=3,column=0,sticky=tk.E)
		self.calc_Dihedral_Label_A = tk.Label(self.calc_Dihedral_frame,text='Atom 1',fg='red')
		self.calc_Dihedral_Label_A.grid(row=0,column=1,sticky=tk.E+tk.W)
		self.calc_Dihedral_Label_B = tk.Label(self.calc_Dihedral_frame,text='Atom 2',fg='blue')
		self.calc_Dihedral_Label_B.grid(row=0,column=2,sticky=tk.E+tk.W)
		self.calc_Dihedral_Label_C = tk.Label(self.calc_Dihedral_frame,text='Atom 3',fg='green3')
		self.calc_Dihedral_Label_C.grid(row=0,column=3,sticky=tk.E+tk.W)
		self.calc_Dihedral_Label_C = tk.Label(self.calc_Dihedral_frame,text='Atom 4',fg='orange')
		self.calc_Dihedral_Label_C.grid(row=0,column=4,sticky=tk.E+tk.W)
	
		self.calc_Dihedral_SelA_Chain = tk.StringVar()
		self.calc_Dihedral_SelA_Res = tk.IntVar()
		self.calc_Dihedral_SelA_Atom = tk.StringVar()
		self.calc_Dihedral_SelA_Atom.set('CA')
		self.calc_Dihedral_SelB_Chain = tk.StringVar()
		self.calc_Dihedral_SelB_Res = tk.IntVar()
		self.calc_Dihedral_SelB_Atom = tk.StringVar()
		self.calc_Dihedral_SelB_Atom.set('CA')
		self.calc_Dihedral_SelC_Chain = tk.StringVar()
		self.calc_Dihedral_SelC_Res = tk.IntVar()
		self.calc_Dihedral_SelC_Atom = tk.StringVar()
		self.calc_Dihedral_SelC_Atom.set('CA')
		self.calc_Dihedral_SelD_Chain = tk.StringVar()
		self.calc_Dihedral_SelD_Res = tk.IntVar()
		self.calc_Dihedral_SelD_Atom = tk.StringVar()
		self.calc_Dihedral_SelD_Atom.set('CA')

		self.calc_Dihedral_SelA_Chain_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelA_Chain,width=2)
		self.calc_Dihedral_SelA_Chain_Entry.grid(row=1,column=1,sticky=tk.W)
		self.calc_Dihedral_SelA_Res_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelA_Res,width=4)
		self.calc_Dihedral_SelA_Res_Entry.grid(row=2,column=1,sticky=tk.W)
		self.calc_Dihedral_SelA_Atom_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelA_Atom,width=3)
		self.calc_Dihedral_SelA_Atom_Entry.grid(row=3,column=1,sticky=tk.W)
		self.calc_Dihedral_SelB_Chain_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelB_Chain,width=2)
		self.calc_Dihedral_SelB_Chain_Entry.grid(row=1,column=2,sticky=tk.W)
		self.calc_Dihedral_SelB_Res_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelB_Res,width=4)
		self.calc_Dihedral_SelB_Res_Entry.grid(row=2,column=2,sticky=tk.W)
		self.calc_Dihedral_SelB_Atom_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelB_Atom,width=3)
		self.calc_Dihedral_SelB_Atom_Entry.grid(row=3,column=2,sticky=tk.W)
		self.calc_Dihedral_SelC_Chain_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelC_Chain,width=2)
		self.calc_Dihedral_SelC_Chain_Entry.grid(row=1,column=3,sticky=tk.W)
		self.calc_Dihedral_SelC_Res_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelC_Res,width=4)
		self.calc_Dihedral_SelC_Res_Entry.grid(row=2,column=3,sticky=tk.W)
		self.calc_Dihedral_SelC_Atom_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelC_Atom,width=3)
		self.calc_Dihedral_SelC_Atom_Entry.grid(row=3,column=3,sticky=tk.W)
		self.calc_Dihedral_SelD_Chain_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelD_Chain,width=2)
		self.calc_Dihedral_SelD_Chain_Entry.grid(row=1,column=4,sticky=tk.W)
		self.calc_Dihedral_SelD_Res_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelD_Res,width=4)
		self.calc_Dihedral_SelD_Res_Entry.grid(row=2,column=4,sticky=tk.W)
		self.calc_Dihedral_SelD_Atom_Entry = tk.Entry(self.calc_Dihedral_frame,textvariable=self.calc_Dihedral_SelD_Atom,width=3)
		self.calc_Dihedral_SelD_Atom_Entry.grid(row=3,column=4,sticky=tk.W)
		
		self.calc_Dihedral_image = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__),'image_dihedral.gif'))
		self.calc_Dihedral_imageLabel = tk.Label(self.calc_Dihedral_frame,image=self.calc_Dihedral_image)
		self.calc_Dihedral_frame.grid_columnconfigure(5,weight=1)
		self.calc_Dihedral_imageLabel.grid(row=1,column=5,rowspan=3,sticky=tk.E,padx=5)
	
	#
	# Action functions
	#
	
	def startCalculator(self):
		"""Depending upon which attribute calculation pane was selected last, initialize the calculator parallelization object and pass it the calculation function to use
		Also set the tkinter callback to update the calculation status"""
		if self.calc_RMSD_Button.cget('default') == tk.ACTIVE:
			args = tools_rmsd.setup(self)
			if args != None:
				self.Calculator = FunctionParallelizer( function=tools_rmsd.calculate, args=args, threads=self.prefs['cpu_count'])
				self.calculatorTitle = "RMSD_to_%s"%(os.path.basename(os.path.splitext(self.calc_RMSD_PDBPath.get())[0]))
		elif self.calc_Rg_Button.cget('default') == tk.ACTIVE:
			args = tools_geom.setup_rg(self)
			if args != None:
				self.Calculator = FunctionParallelizer( function=tools_geom.calculate_rg, args=args, threads=self.prefs['cpu_count'])
				self.calculatorTitle = "Rg"
		elif self.calc_Distance_Button.cget('default') == tk.ACTIVE:
			args = tools_geom.setup_distance(self)
			if args != None:
				self.Calculator = FunctionParallelizer( function=tools_geom.calculate_distance, args=args, threads=self.prefs['cpu_count'])
				self.calculatorTitle = "%s%i%s-%s%i%s"%tuple(args[0]+args[1])
		elif self.calc_Angle_Button.cget('default') == tk.ACTIVE:
			args = tools_geom.setup_angle(self)
			if args != None:
				self.Calculator = FunctionParallelizer( function=tools_geom.calculate_angle, args=args, threads=self.prefs['cpu_count'])
				self.calculatorTitle = "%s%i%s-%s%i%s-%s%i%s"%tuple(args[0]+args[1]+args[2])
		elif self.calc_Dihedral_Button.cget('default') == tk.ACTIVE:
			args = tools_geom.setup_dihedral(self)
			if args != None:
				self.Calculator = FunctionParallelizer( function=tools_geom.calculate_dihedral, args=args, threads=self.prefs['cpu_count'])
				self.calculatorTitle = "%s%i%s-%s%i%s-%s%i%s-%s%i%s"%tuple(args[0]+args[1]+args[2]+args[3])

		if args != None:
			self.Calculator.put(self.pdbList)
			self.calculatorFile = tempfile.TemporaryFile()
			self.calculatorAfter = self.after( _PDB_calculator_timer, self.updateCalculator )
			self.calculatorCounter = 0
	
	def updateCalculator(self):
		"""Update the calculation status, and re-set the tkinter callback for the next update"""
		for ok,(pdb,info) in self.Calculator.get():
			if ok:
				self.calculatorFile.write("%s\t%s\n"%(os.path.basename(os.path.splitext(pdb)[0]),info))
			else:
				tkMessageBox.showerror("Error","Error on PDB %s:\n\nReason:\n%s"%(pdb,info),parent=self)
				self.stopCalculator(abort=True)
				return
			self.calculatorCounter += 1

		if self.calculatorCounter == len(self.pdbList):
			insert_attribute_column(self,self.calculatorFile,col_title=self.calculatorTitle)
			self.stopCalculator() # this closes the self.calculatorFile handle
			self.setAttributeTable(new=False,path=self.attributeFilePath.get())
			self.updateAttributeInfo("Done.")
		else:
			self.updateAttributeInfo("Processing PDB %i of %i."%(self.calculatorCounter,len(self.pdbList)))
			self.calculatorAfter = self.after( _PDB_calculator_timer, self.updateCalculator )
		
	def stopCalculator(self,abort=False):
		"""Stop the window's calculator.
		
		Args:
			abort (bool): Force the calculator to stop (ungracefully?)
		
		Returns: None"""
		if self.Calculator != None:
			self.calculatorFile.close()
			if abort:
				self.after_cancel(self.calculatorAfter)
				self.Calculator.abort()
				self.updateAttributeInfo("Aborted.")
			else:
				self.Calculator.stop()
			self.Calculator = None
							
	def _reset_menu_options(self,optionmenu,optionvar,options,index=None):
		"""Reset a tkinter OptionMenu and associated variable
		
		Args:
			optionmenu (tkinter OptionMenu): The menu to set with new options
			optionvar (tkinter variable): The variable associated with the optionmenu
			options (list): A list of options to load into the new menu
			index (int): Which index to set as the currently-selected item, defaults to None
		
		Returns: None"""
		optionmenu["menu"].delete(0, "end")
		for string in options:
			optionmenu["menu"].add_command(label=string, command=lambda value=string: optionvar.set(value))
		if index is not None:
			optionvar.set(options[index])
			
	def updateAttributeInfo(self,text):
		"""Update the window's status text
		
		Args:
			text (string): The text to display
			
		Returns: None"""
		self.attributeFileInfo.config(text=text)
		self.update_idletasks()
			
	def updateCalculateButton(self):
		"""Set the calculation button to enabled or disabled if there's a valid list of PDBs present, and the attribute table is loaded
		If the RMSD attribute calculation button is active, make sure there's a valid reference PDB too"""
		if len(self.pdbList) > 0 and self.attributeFilePath.get() != '':
			if self.calc_RMSD_Button.cget('default') == tk.ACTIVE and self.calc_RMSD_PDBPath.get() == '':
				self.calculateButton.config(state=tk.DISABLED)
			else:
				self.calculateButton.config(state=tk.NORMAL)
		else:
			self.calculateButton.config(state=tk.DISABLED)
			
	def loadDirPDBs(self,path=''):
		"""Set the directory containing PDBs."""
		if path == '':
			path = tkFileDialog.askdirectory(title="Choose a directory containing PDBs:",parent=self)
		if path == '':
			return
	
		self.pdbDirectoryInfo.config(text="Scanning directory...")
		self.update_idletasks()
		self.pdbList = glob.glob(os.path.join(path,"*.pdb"))
		self.pdbList.sort()
		
		if len(self.pdbList) == 0:
			if tkMessageBox.askyesno("Empty","There are no readable PDBs in this directory. Try another?",parent=self):
				self.loadDirPDBs()
			else:
				self.pdbDirectoryInfo.config(text="Error.")
				self.update_idletasks()
		
		self.pdbDirectoryInfo.config(text="Loaded %i coordinate files."%(len(self.pdbList)))
		self.update_idletasks()
		self.pdbDirectoryPath.set(path)
		self.pdbDirectoryEntry.xview_moveto(1.0)
		
		self.attributeFileSetButton.config(state=tk.NORMAL)
		self.attributeFileNewButton.config(state=tk.NORMAL)
		self.updateCalculateButton()

	def setAttributeTable(self,new=False,path=''):
		"""Loads either an existing attribute table, or creates a new one.
		
		Args:
			new (bool): Create a new table?
			path (string): Path to an existing attribute table to load. If not provided, prompts the user.
			
		Returns: None"""
		# @TODO@ Check loaded PDBs against selected table?
		if path == '':
			if new:
				path = tkFileDialog.asksaveasfilename(title='Create new attribute table:',filetypes=[('Attr',"*.attr"),('Text',"*.txt"),('Table',"*.tbl")],initialfile="pdb_attributes.txt",parent=self)
			else:
				path = tkFileDialog.askopenfilename(title='Attribute table to append to:',filetypes=[('Attr',"*.attr"),('Text',"*.txt"),('Table',"*.tbl")],parent=self)
		if path == '':
			return
				
		if new:
			self.updateAttributeInfo("Creating table...")
			try:
				f = open( path, 'w' )
				f.write("#pdb\n")
				for pdb in self.pdbList:
					f.write( "%s\n"%(os.path.basename(os.path.splitext(pdb)[0])) )
				f.close()
			except:
				tkMessageBox.showerror("Error","Could not open the table for writing.",parent=self)
				self.updateAttributeInfo("Error.")
				return

			pdbcounter = len(self.pdbList)
			self.attributeFileColumns = []
		else:	
			self.updateAttributeInfo("Scanning table...")
			try:
				header,rows,columns = get_table_info(path)
			except Exception as e:
				tkMessageBox.showerror("Error","Error opening the specified table: %s"%(e),parent=self)
				self.updateAttributeInfo("Error.")
				return
			
			if rows != len(self.pdbList):
				tkMessageBox.showerror("Error","The selected table does not have a corresponding number of entries for the provided PDB directory!",parent=self)
				self.updateAttributeInfo("Error.")
				return
						
			if header != None:
				self.attributeFileColumns = header[1:]
			else:
				tkMessageBox.showerror("Error","Attribute table doesn't contain column header.\ne.g.: #pdb    col1    col2    etc...",parent=self)
				self.updateAttributeInfo("Error.")
				return
				
			if len(header) != len(set(header)):
				tkMessageBox.showwarning("Warning","Attribute table has duplicate column headers. Unexpected behavior may occur!",parent=self)
				
		self.attributeFileColumns.append("(Append new)")

		self._reset_menu_options(self.attributeFileColMenu,self.attributeFileColSel,self.attributeFileColumns,len(self.attributeFileColumns)-1)
		self.attributeFileColMenu.config(state=tk.NORMAL)

		if new:
			self.updateAttributeInfo("Created new table with %i records."%(pdbcounter))
		elif len(self.attributeFileColumns)-1 == 1:
			self.updateAttributeInfo("Loaded table with %i records, 1 attribute."%(rows))		
		else:
			self.updateAttributeInfo("Loaded table with %i records, %i attributes."%(rows,len(self.attributeFileColumns)-1))

		self.attributeFilePath.set(path)
		self.attributeFileEntry.xview_moveto(1.0)
		self.updateCalculateButton()
			
	def setRMSDReference(self,tmp=''):
		"""Sets the RMSD reference PDB.
		
		Args:
			tmp (string): Path to an existing PDB. If not provided, prompts the user.
		
		Returns: None"""
		if tmp == '':
			tmp = tkFileDialog.askopenfilename(title='PDB coordinate file to use as a reference:',parent=self,filetypes=[('PDB',"*.pdb")])
		if tmp == '':
			return
		self.calc_RMSD_PDBPath.set(tmp)
		self.calc_RMSD_PDBEntry.xview_moveto(1.0)
		self.updateCalculateButton()
