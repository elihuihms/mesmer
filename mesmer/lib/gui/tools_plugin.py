import inspect
import tkMessageBox

from .. exceptions			import *
from .. plugin_functions	import load_plugins
from .. setup_functions		import set_default_prefs

def tryLoadPlugins( shelf, type, args=None, disabled_writeback=False ):

	plugins,disabled = [],shelf['disabled_plugins'][:] # (copy slicing isn't necessary if shelf is actually a shelf)
	for id,ok,msg,module in load_plugins( shelf['mesmer_base_dir'], type, disabled=disabled, args=args ):
		if ok:
			plugins.append( module )
		else:
			disabled.append( id )

	if disabled_writeback:
		shelf['disabled_plugins'] = list(set(disabled)) # uniquify
		
	return plugins	

def getTargetPluginOptions( plugins, prefs ):
	types, options = [], []
	for p in plugins:
		types.append( [] )
		for t in p.types:
			if( not t[0:4] in types[-1] ):
				types[-1].append(t[0:4])
		options.append( convertParserToOptions(p.target_parser) )
	return types,options

def getPluginPrefs( shelf, name ):
	try:
		plugin_prefs = shelf['plugin_prefs']
	except KeyError:
		set_default_prefs( shelf )
		return getPluginPrefs( shelf, name )
	if name not in plugin_prefs:
		plugin_prefs[name] = {'options':{},'path':None}
	return plugin_prefs[name]
	
def setPluginPrefs( shelf, name, **kwargs ):
	plugin_prefs = shelf['plugin_prefs']
	if name not in plugin_prefs:
		plugin_prefs[name] = getPluginPrefs( shelf, name )

	for key,value in kwargs.iteritems():
		plugin_prefs[name][key] = value
		
	try:
		shelf['plugin_prefs'] = plugin_prefs
		shelf.sync()
	except:
		tkMessageBox.showerror("Error",'Failed to save preferences. Perhaps user folder is read only?')
		raise
		
def convertParserToOptions( parser ):
	"""Convert an argparse argument parser to a descriptive dict
	
	Args:
		parser (argparse.ArgumentParser): Parser to construct dict from
	
	Returns: dict representation of parser"""
	
	options,savetypes = [],('help','option_strings','choices','type','dest','default','choices','required','nargs','metavar')
	for action in [a.__dict__ for a in parser.__dict__['_actions']]:
		if action['dest'] == 'help':
			continue
		options.append( {} )
		for key in savetypes:
			options[ -1 ][ key ] = action[ key ]
		options[ -1 ]['value'] = ''
		options[ -1 ]['group'] = action['container'].title

	return options

def makeListFromOptions( options ):
	ret = []
	for o in options:
		if(o['nargs'] == 0):
			if o['value']:
				ret.append( o['option_strings'][0] )
		elif( o['value'] == None or o['value'] == 'None' or o['value'] == '' ):
			if o['required']:
				raise Exception("Encountered a required option without a value: %s" % o['dest'])
		elif(o['nargs'] == None):
			ret.append( o['option_strings'][0] )
			ret.append( str(o['value']) )
		else:
			raise Exception("Encountered an option that could not be converted to a string properly: %s" % o['dest'])
	return ret
	
def makeDictFromOptions( options ):
	
	
def setOptionsFromBlock( options, block ):
	header = block['header'].split()

	for o in options:

		if(o['nargs'] == 0):
			o['value'] = (o['option_strings'][0] in header[2:])
			continue

		if( not o['option_strings'][0] in header[2:]):
			continue
		else:
			i = header.index(o['option_strings'][0])+1

		if(i > len(header)):
			raise Exception("Header to short to contain a value for key: %s" % o['dest'])
		elif(header[i][0] == o['option_strings'][0][0]):
			raise Exception("Header missing a value for key: %s" % o['dest'])

		if(o['nargs'] == None):
			if(o['type'] == type(0)):
				o['value'] = int( header[i] )
			elif(o['type'] == type(0.0)):
				o['value'] = float( header[i] )
			else:
				o['value'] = header[i]

		else:
			raise Exception("Encountered an option that could not be parsed properly: %s" % o['dest'])
	return options
