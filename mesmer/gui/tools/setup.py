import os
import Tkinter as tk
import tkFileDialog

from .. setup_functions	import parse_arguments

def makeStringFromArgs( a ):
	args = vars( a )

	""" @TODO@ Make this general purpose and move to tools_plugin """
	ret = []
	booleans = ('Rforce','Pstats','Pbest','Popt','Pextra','Pstate','force','uniform','resume','dbm','reset')
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