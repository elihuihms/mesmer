#!/usr/bin/env python

import Tkinter as tk
import argparse

from tools_TkTooltip import ToolTip
from plugin_functions import convertParserToDict

parser = argparse.ArgumentParser(fromfile_prefix_chars='@')

group0 = parser.add_argument_group('Target and component files')
group0.add_argument('-target',		action='append',	required=(str==None),					metavar='FILE.target',			help='MESMER target file')
group0.add_argument('-components',	action='append',	required=(str==None),	nargs='*',		metavar='FILE.component/DIR',	help='MESMER component files or directory ')
group0.add_argument('-resume',															metavar='STATE.tbl',			help='Resume from a provided ensemble state')

group1 = parser.add_argument_group('Simulation size and convergence parameters')
group1.add_argument('-name',		action='store',		default='MESMER_Results',		metavar='NAME',	help='Name of this run - a directory will be created with this name to contain all MESMER output')
group1.add_argument('-dir',			action='store',		default='./',					metavar='DIR',	help='Directory in which to create results folder')
group1.add_argument('-ensembles',	action='store',		default=1000,	type=int,		metavar='N',	help='Number of ensembles to use in the algorithm')
group1.add_argument('-size',		action='store',		default=3,		type=int,		metavar='N',	help='Number of components per ensemble')
group1.add_argument('-Fmin',		action='store',		default=-1,		type=float,		metavar='F',	help='Maximum ensemble fitness to stop algorithm')
group1.add_argument('-Smin',		action='store',		default=0,		type=float,		metavar='F',	help='Minimum ensemble fitness stdev to stop algorithm')

group2 = parser.add_argument_group('Genetic algorithm coefficients')
group2.add_argument('-Gmax',		action='store',		default=-1,		type=int,		metavar='N',	help='Maximum number of generations, set to -1 to run indefinitely')
group2.add_argument('-Gcross',		action='store',		default=0.8,	type=float,		metavar='F',	help='Ensemble component crossing frequency')
group2.add_argument('-Gmutate',		action='store',		default=1.0,	type=float,		metavar='F',	help='Ensemble component mutation frequency')
group2.add_argument('-Gsource',		action='store',		default=0.1,	type=float,		metavar='F',	help='Ensemble component mutation source frequency')

group3 = parser.add_argument_group('Variable component ratio parameters')
group3.add_argument('-Rforce'	,	action='store_true',default=False,									help='Force ensemble ratio reoptimization at every generation.')
group3.add_argument('-Ralgorithm',	action='store',		default=3,	type=int,	choices=[0,1,2,3,4,5,6],	metavar='N',	help='Algorithm to use for optimal component ratios (0-6), 0=no ratio optimization')
group3.add_argument('-Rprecision',	action='store',		default=0.01,	type=float,		metavar='F',	help='Precision of weighting algorithm')
group3.add_argument('-Rn',			action='store',		default=-1,		type=int,		metavar='N',	help='Number of weighting algorithm iterations')
group3.add_argument('-boots',		action='store',		default=200,	type=int,		metavar='N',	help='The number of bootstrap samples for component weighting error analysis. 0=no error analysis')

group4 = parser.add_argument_group('Output options')
group4.add_argument('-Pstats',		action='store_true',default=True,									help='Print ensemble information at each generation. NOTE: always enabled')
group4.add_argument('-Pbest',		action='store_true',default=True,									help='Print best ensemble information at each generation.')
group4.add_argument('-Popt',		action='store_true',default=False,									help='Print optimization convergence status for all ensembles.')
group4.add_argument('-Pextra',		action='store_true',default=False,									help='Print extra restraint-specific information.')
group4.add_argument('-Pstate',		action='store_true',default=False,									help='Print ensemble ratio state at each generation')
group4.add_argument('-Pmin',		action='store',		default=1.0,	type=float,		metavar='F',	help='Print conformer statistics only if they exist in this percentage of ensembles or greater.')
group4.add_argument('-Pcorr',		action='store',		default=1.0,	type=float,		metavar='F',	help='Print conformer correlations only if they exist in this percentage of ensembles or greater.')

group5 = parser.add_argument_group('Miscellaneous options')
group5.add_argument('-seed',		action='store',		default=1,		type=int,		metavar='N',	help='Random number generator seed value to use.')
group5.add_argument('-uniform',		action='store_true',default=False,									help='Load ensembles uniformly from available components instead of randomly')
group5.add_argument('-force',		action='store_true',default=False,									help='Enable overwriting of previous output directories.')
group5.add_argument('-threads',		action='store',		default=1,		type=int,		metavar='N',	help='Number of multiprocessing threads to use.')
group5.add_argument('-dbm',			action='store_true',default=False,									help='Use a component database instead of maintaining in memory (much slower, significantly reduced memory footprint')
group5.add_argument('-plugin',		action='store',										metavar='NAME',	help='Print information about the specified plugin and exit.')


def setOptionsFromBlock( options, block ):
	header = block['header'].split()

	for k in self.options:
		if(self.options[k]['type'] == None and self.options[k]['choices'] != None):
			# boolean option
			if( ('-%s' % opt) in header[2:] ):
				self.options[k]['value'] = 1
			else:
				self.options[k]['value'] = 0
		else:
			self.options[k]['value'] = header.index(('-%s' % opt))+1

	return options

class OptionsWindow(tk.Frame):
	def __init__(self, master, index, options):
		self.master = master
		self.master.title('Set Options')
		self.master.resizable(width=False, height=False)

		self.index = index
		self.options = options

		tk.Frame.__init__(self,master)

		self.grid()
		self.createWidgets()

	def saveWindow(self):
		# retrieve the set values, save back to the options dict
		for (i,k) in enumerate(self.options):
			self.options[k]['value'] = self.optionValues[i].get()

		# send the modified options back to the calling window
		self.callback(self.index, self.options)
		self.master.destroy()

	def cancelWindow(self):
		self.master.destroy()

	def createWidgets(self):

		self.container = tk.Frame(self)
		self.container.grid(in_=self,padx=6,pady=6)

		self.optionLabels	= []
		self.optionToolTips	= []
		self.optionValues	= []
		self.optionEntries	= []

		rowCounter = 0
		for k in self.options:
			option = self.options[k]
			if(not 'value' in option.keys()):
				option['value'] = option['default']

			self.optionLabels.append( tk.Label(self.container,text=option['dest'].capitalize()) )
			self.optionLabels[-1].grid(in_=self.container,column=0,row=rowCounter,sticky=tk.W)
			self.optionToolTips = ToolTip(self.optionLabels[-1],follow_mouse=0,text=option['help'])

			if(option['choices'] != None):
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set( option['value'] )
				self.optionEntries.append( tk.OptionMenu(self.container,self.optionValues[-1],*option['choices']) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			elif(option['type'] == None):
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
			elif(option['type'] == type('')):
				self.optionValues.append( tk.StringVar() )
				self.optionValues[-1].set(option['value'])
				self.optionEntries.append( tk.Entry(self.container,textvariable=self.optionValues[-1],width=12) )
				self.optionEntries[-1].grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W)
			rowCounter+=1

		self.cancelButton = tk.Button(self.container,text='Cancel',command=self.cancelWindow)
		self.cancelButton.grid(in_=self.container,column=0,row=rowCounter,sticky=tk.E,pady=8)
		self.saveButton = tk.Button(self.container,text='Save',command=self.saveWindow,default=tk.ACTIVE)
		self.saveButton.grid(in_=self.container,column=1,row=rowCounter,sticky=tk.W,pady=8)

opts = convertParserToDict(parser)
root = tk.Tk()
app = OptionsWindow(root,0,opts)
app.mainloop()