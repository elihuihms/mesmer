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
	This is a very horrible function.
	It returns descriptive dictionary of arguments from an argparse parser by inspecting the parser._actions dictionary of functions and extracting their arguments.
	"""

	savetypes = ('help','option_strings','choices','type','dest','default','choices','required','nargs')

	args = {}
	for a in parser._actions:

		m = inspect.getmembers(a)
		for e in m:
			if(e[0] == 'dest'):
				keys = zip(*m)[0]
				vals = zip(*m)[1]

				try:
					k = vals[keys.index('dest')]
				except:
					break

				args[ k ] = {}
				for i in range(len(keys)):
					if( keys[i] in savetypes ):
						args[k][ keys[i] ] = vals[i]

	del args['help']
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