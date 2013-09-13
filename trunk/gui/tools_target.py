from lib.plugin_functions	import load_plugins
from gui.tools_plugin		import convertParserToOptions

def getPluginOptions( path ):
	try:
		plugins = load_plugins

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

def makeStringFromOptions( options ):
	string = ''

	for k in options:
		if( not 'value' in options[k] ):
			if options[k]['required']:
				raise Exception("Encountered a required option without a value: %s" % options[k]['dest'])
		elif( options[k]['value'] == None or options[k]['value'] == 'None' ):
			if options[k]['required']:
				raise Exception("Encountered a required option without a value: %s" % options[k]['dest'])
			continue
		elif(options[k]['nargs'] == 0):
			if(options[k]['value']):
				string+="%s " % options[k]['option_strings'][0]
		elif(options[k]['nargs'] == None):
			string+="%s %s " % (options[k]['option_strings'][0],options[k]['value'])
		else:
			raise Exception("Encountered an option that could not be converted to a string properly: %s" % options[k]['dest'])

	return string

def extractDataFromFile( file ):
	try:
		f = open( file )
	except:
		tkMessageBox.showerror("Missing Data","There was an error reading the data file \"%s\"" % (file),parent=self)
		return None

	text = ''
	for l in f.readlines():
		if(l.strip() != ''):
			text+="%s\n" % l.strip()

	return text

def makeTargetFromWindow( w ):
	name	= w.targetName.get().replace(' ','_')
	text = "NAME\t%s\n#\t%s\n\n" % (name,w.targetComments.get())

	type_counters = {}
	for i in range(w.rowCounter):
		type	= w.widgetRowTypes[i].get()
		weight	= w.widgetRowWeights[i].get()
		opts	= makeStringFromOpts( w.widgetRowOptions[i][type] )
		data	= extractDataFromFile( w.widgetRowFiles[i].get() )
		if( data == None ):
			return None

		if(type in type_counters):
			type_counters[type]+=1
		else:
			type_counters[type]=0

		text+="%s%i\t%f\t%s\n%s\n\n" % (type,type_counters[type],weight,opts,data)

	return text