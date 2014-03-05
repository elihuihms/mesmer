import inspect
import tkMessageBox

from .. exceptions			import *
from .. plugin_functions	import load_plugins
from .. setup_functions		import parse_arguments

def getTargetPluginOptions( path ):
	try:
		plugins = load_plugins( path, 'mesmer', parse_arguments('') )
	except mesPluginError as e:
		tkMessageBox.showerror("Error",'Failed to load one or more MESMER plugins: %s' % (e.msg))

	types, options = [], []
	for p in plugins:
		types.append( [] )
		for t in p.type:
			if( not t[0:4] in types[-1] ):
				types[-1].append(t[0:4])
		options.append( convertParserToOptions(p.target_parser) )

	return (types,options)

def getGUICalcPlugins( path ):
	try:
		plugins = load_plugins( path, 'gui_c' )
	except mesPluginError as e:
		tkMessageBox.showerror("Error",'Failed to load one or more GUI data plugins: %s' % (e.msg))

	if(len(plugins) == 0):
		raise Exception('No GUI calculation plugins found')

	return plugins

def getGUIPlotPlugins( path ):
	try:
		plugins = load_plugins( path, 'gui_p' )
	except mesPluginError as e:
		tkMessageBox.showerror("Error",'Failed to load one or more GUI plot plugins: %s' % (e.msg))

	if(len(plugins) == 0):
		raise Exception('No GUI plotting plugins found')

	return plugins

def convertParserToOptions( parser ):
	"""
	Returns a descriptive dictionary of arguments from an argparse parser by inspecting the parser._actions dictionary of functions and extracts its arguments.
	This could cause problems in the future, as it relies upon reading the private methods of the external argparse ArgumentParser object.
	"""

	# do some basic sanity checks to make sure we can access the parser actions
	try:
		tmp = parser._actions
		if(len(tmp)>0):
			inspect.getmembers( tmp[0] )
	except:
		raise Exception("Could not inspect parser actions. Please report this bug!")

	# what information from the inspection object will we save? 
	savetypes = ('help','option_strings','choices','type','dest','default','choices','required','nargs')
				
	args = {}
	for action in parser._actions:
		members = inspect.getmembers(action)

		for (k,v) in members:
			if(k == 'dest'): # check that the action sets a destination variable. If it's not, ignore it.
				keys = zip(*members)[0]
				vals = zip(*members)[1]

				args[v] = {}
				for i in range(len(keys)):
					if( keys[i] in savetypes ):
						args[v][ keys[i] ] = vals[i]
						
				break # go to the next action

	del args['help']

	# set the default value for each argument	
	for k in args:
		args[k]['value'] = args[k]['default']
		if(args[k]['value'] == None): args[k]['value'] = ''

	return args

def setOptionsFromBlock( options, block ):
	header = block['header'].split()

	for k in options:

		if(options[k]['nargs'] == 0):
			options[k]['value'] = (options[k]['option_strings'][0] in header[2:])
			continue

		if( not options[k]['option_strings'][0] in header[2:]):
			continue
		else:
			i = header.index(options[k]['option_strings'][0])+1

		if(i > len(header)):
			raise Exception("Header to short to contain a value for key: %s" % options[k]['dest'])
		elif(header[i][0] == options[k]['option_strings'][0][0]):
			raise Exception("Header missing a value for key: %s" % options[k]['dest'])

		if(options[k]['nargs'] == None):
			if(options[k]['type'] == type(0)):
				options[k]['value'] = int( header[i] )
			elif(options[k]['type'] == type(0.0)):
				options[k]['value'] = float( header[i] )
			else:
				options[k]['value'] = header[i]

		else:
			raise Exception("Encountered an option that could not be parsed properly: %s" % options[k]['dest'])
	return options

def makeListFromOptions( options ):
	ret = []
	for k in options:
		if(not 'value' in options[k]):
			if options[k]['required']:
				raise Exception("Encountered a required option without a value: %s" % options[k]['dest'])
			continue

		if(options[k]['nargs'] == 0):
			if options[k]['value']:
				ret.append( options[k]['option_strings'][0] )
		elif( options[k]['value'] == None or options[k]['value'] == 'None' or options[k]['value'] == '' ):
			if options[k]['required']:
				raise Exception("Encountered a required option without a value: %s" % options[k]['dest'])
		elif(options[k]['nargs'] == None):
			ret.append( options[k]['option_strings'][0] )
			ret.append( str(options[k]['value']) )
		else:
			raise Exception("Encountered an option that could not be converted to a string properly: %s" % options[k]['dest'])
	return ret
	
def makeStringFromOptions( options ):
	return ' '.join( makeListFromOptions(options) )