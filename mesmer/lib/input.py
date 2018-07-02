import shlex

def set_options_from_block( options, block ):
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

def get_input_blocks( file ):
	"""
	Splits a file into blocks for handing off to plugins

	Arguments:
	file	- String containing the path to the file

	block dictionary format:
	type	- string, corresponds to a type handled by this plugin
	header	- string, containing the first line of the content block
	content	- list of strings, containing the rest of the content block (if any)
	l_start	- integer, the line index for the start of the content block from the original file
	l_end	- integer, the line index for the end of the content block from the original file
	"""

	try:
		f = open( file, 'r' )
	except IOError:
		return None

	lines = f.readlines()
	f.close()

	i,blocks = 0,[]
	while( i < len(lines) ):
		data = shlex.split(lines[i])
		
		if len(data) == 0 or data[0] == '#':
			i+=1
			continue

		header,comment = [],''
		for j,d in enumerate(data):
			if d[0] != '#':
				header.append(d)
			else:
				comment = ' '.join(data[j:])
				break
				
		# create a new block with the header line
		blocks.append( {'type':header[0],'header':header,'content':[],'l_start':i,'l_end':i,'comment':comment} )
		
		# append all subsequent non-empty lines to the new block's content until an empty one appears
		i+=1
		while( i < len(lines) and lines[i].strip() != '' ):
			blocks[-1]['content'].append( lines[i] )
			blocks[-1]['l_end'] = i
			i+=1
		i+=1

	return blocks