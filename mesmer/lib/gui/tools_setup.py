import os
import Tkinter as tk
import tkFileDialog

from .. setup_functions	import parse_arguments

def loadControlVarArgs(w):
	tmp = tkFileDialog.askopenfilename(title='Select MESMER run config file:',parent=w)
	if(tmp == ''):
		return
	string = open(tmp).read()
	string.replace("\n",'')
	string.replace("\r",'')
	args = parse_arguments(string)
	setControlVarsFromMESMERArgs(w, args)

def saveControlVarArgs(w):
	text = makeStringFromArgs( makeMESMERArgsFromWindow(w) )
	if(text == None):
		return

	tmp = tkFileDialog.asksaveasfile(title='Select name and location for MESMER config file:',initialfile='args.txt',parent=w)
	if(tmp == None):
		return
	tmp.write(text)
	tmp.close()

def setControlVarsFromMESMERArgs(w, args):
	w.runTitle.set(args.name)
	w.saveResults.set(os.path.normpath(os.path.join(w.basedir,args.dir)))
	if(args.target != None):
		tmp = []
		for f in args.target:
			tmp.append( os.path.normpath(f) )
		w.targetFiles.set(tuple(tmp))
	if(args.components != None):
		tmp = []
		for f in args.components:
			for g in f:
				tmp.append( os.path.normpath(g) )
		w.componentFiles.set(tuple(tmp))
	w.ensembleSize.set(args.size)
	w.numEnsembles.set(args.ensembles)
	w.gCrossFreq.set(args.Gcross)
	w.gMutateFreq.set(args.Gmutate)
	w.gSourceRatio.set(args.Gsource)
	if(args.Fmin>=0):
		w.minFitness.set(args.Fmin)
		w.minFitnessCheck.set(1)
	if(args.Smin>=0):
		w.minRSD.set(args.Smin)
		w.minRSDCheck.set(1)
	if(args.Gmax>=0):
		w.maxGenerations.set(args.Gmax)
		w.maxGenerationsCheck.set(1)
	if(args.Pbest):
		w.bestFitCheck.set(1)
	if(args.Pstats >= 0):
		w.componentStatsCheck.set(1)
		w.componentStats.set(float(args.Pstats))
	if(args.Pcorr < 100):
		w.componentCorrCheck.set(1)
	w.componentCorr.set(args.Pcorr)
	if(args.Pextra):
		w.pluginExtrasCheck.set(1)
	if(args.Popt):
		w.optimizationStateCheck.set(1)
	w.optMethod.set( args.Ralgorithm )
	w.optMethodOption.set( w.optMethodOptions[w.optMethod.get()] )
	w.optTolerance.set(args.Rprecision)
	w.optIterations.set(args.Rn)

	w.setCheckboxStates()
	w.setButtonStates()

def makeMESMERArgsFromWindow( w ):

	# get any machine-specific arguments
	pre_args = []
	if(w.prefs.has_key('run_arguments')):
		tmp = w.prefs['run_arguments']
		for k in tmp:
			pre_args.extend( ["-%s" % k, str(tmp[k])] )

	args = parse_arguments( ' '.join(pre_args) )
	args.name = w.runTitle.get().replace(' ','_')
	args.dir = w.saveResults.get()
	args.target = list(w.targetFilesList.get(0,tk.END)) #see bug notice in createControlVars
	args.components = list(w.componentFilesList.get(0,tk.END)) #see bug notice in createControlVars
	args.size = w.ensembleSize.get()
	args.ensembles = w.numEnsembles.get()
	args.Gcross = w.gCrossFreq.get()
	args.Gmutate = w.gMutateFreq.get()
	args.Gsource = w.gSourceRatio.get()
	if(w.minFitnessCheck.get()>0):
		args.Fmin = w.minFitness.get()
	else:
		args.Fmin = None
	if(w.minRSDCheck.get()>0):
		args.Smin = w.minRSD.get()
	else:
		args.Smin = None
	if(w.maxGenerationsCheck.get()>0):
		args.Gmax = w.maxGenerations.get()
	else:
		args.Gmax = None
	args.Pbest = (w.bestFitCheck.get()>0)
	args.Popt = (w.optimizationStateCheck.get()>0)
	args.Pextra = (w.pluginExtrasCheck.get()>0)
	if(w.componentStatsCheck.get()>0):
		args.Pstats = True
		args.Pmin = w.componentStats.get()
	else:
		args.Pstats = False
		args.Pmin = None
	if(w.componentCorrCheck.get()>0):
		args.Pcorr = w.componentCorr.get()
	else:
		args.Pcorr = 100
	try:
		args.Ralgorithm = w.optMethodOptions.index(w.optMethodOption.get())
	except:
		args.Ralgorithm = 0
	args.Rprecision = w.optTolerance.get()
	args.Rn = w.optIterations.get()

	return args

def makeStringFromArgs( a ):
	args = vars( a )

	ret = []
	booleans = ('Rforce','Pstats','Pbest','Popt','Pextra','Pstate','force','uniform','resume','dbm')
	for k in args:
		if(k in booleans):
			if(args[k]>0):
				ret.append( "-%s" % k )
		elif(isinstance(args[k],(list,tuple))):
			for w in args[k]:
				ret.append( "-%s %s" % (k,w) )
		elif(isinstance(args[k],(str,basestring))):
			ret.append( "-%s %s" % (k,args[k]) )
		elif(isinstance(args[k],float)):
			ret.append( "-%s %f" % (k,args[k]) )
		elif(isinstance(args[k],int)):
			ret.append( "-%s %i" % (k,args[k]) )

	return "\n".join(ret)