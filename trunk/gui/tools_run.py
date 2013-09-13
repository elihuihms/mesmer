import Tkinter as tk

from lib.setup_functions	import parse_arguments

def makeMESMERArgsFromWindow(w):
	args = parse_arguments('')
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
	args.Popt = (w.optimizationStateCheck.get()>0)
	try:
		args.Ralgorithm = w.optMethodOptions.index(w.optMethodOption.get())
	except:
		args.Ralgorithm = 0
	args.Rprecision = w.optTolerance.get()
	args.Rn = w.optIterations.get()

	# get any machine-specific arguments
	if(w.prefs.has_key('run_arguments')):
		p_args = w.prefs['run_arguments']
		for k in p_args: #don't overwrite any arguments already explicitly specified
			if not k in args:
				args[k] = p_args[k]

	args = vars(args)

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