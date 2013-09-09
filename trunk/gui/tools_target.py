import tkMessageBox

def makeStringFromOpts( opts ):
	string = ''
	for i in range(len(opts['bool_options'])):
		(name,opt,value,help) = opts['bool_options'][i]
		if(value>0):
			string+="-%s " % (opt)

	for i in range(len(opts['int_options'])):
		(name,opt,value,help) = opts['int_options'][i]
		if(value!=None):
			string+="-%s %i " % (opt,value)

	for i in range(len(opts['float_options'])):
		(name,opt,value,help) = opts['float_options'][i]
		if(value!=None):
			string+="-%s %f" % (opt,value)

	for i in range(len(opts['string_options'])):
		(name,opt,value,help) = opts['string_options'][i]
		if(value!=''):
			string+="-%s %f" % (opt,value)

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