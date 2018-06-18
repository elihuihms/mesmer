import inspect
import tkMessageBox
import collections

from .. exceptions			import *
from .. plugin_functions	import load_plugins,dict_from_parser
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
		options.append( dict_from_parser(p.target_parser) )
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

def setOptionsFromBlock( options, block ):
	for k,o in options.iteritems():

		if(o['nargs'] == 0):
			o['value'] = (o['option_strings'][0] in block['header'][2:])
			continue

		if( not o['option_strings'][0] in block['header'][2:]):
			continue
		else:
			i = block['header'].index(o['option_strings'][0])+1

		if(i > len(block['header'])):
			raise Exception("Header to short to contain a value for key: %s" % o['dest'])
		elif(block['header'][i][0] == o['option_strings'][0][0]):
			raise Exception("Header missing a value for key: %s" % o['dest'])

		if(o['nargs'] == None):
			if(o['type'] == type(0)):
				o['value'] = int( block['header'][i] )
			elif(o['type'] == type(0.0)):
				o['value'] = float( block['header'][i] )
			else:
				o['value'] = block['header'][i]

		else:
			raise Exception("Encountered an option that could not be parsed properly: %s" % o['dest'])
	return options
