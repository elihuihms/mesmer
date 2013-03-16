import re
import math

# global for storing the last message file used
_lastMsgFile = None

def print_msg( text, file=None, NL=True ):
	"""
	Prints a provided message to both stdout and appends it to provided filename
	If a _lstMsgFile is present in the existing namespace, the file argument can be left blank, and this will be used instead.
	
	Returns True on success or False on failure
	
	Arguments:
	text	- String, the text to be printed
	file	- String, the file (path) to save the text to
	NL		- Boolean, should a newline be appended to the text?
	"""
	
	global _lastMsgFile
	
	if( NL ):
		text = "%s\n" % (text)
	
	if( (_lastMsgFile != None) and (file == None) ):
		file = _lastMsgFile
		
	_lastMsgFile = file
	if( file != None ):
		try:
			handle = open( file, 'a' )
			handle.write( text )
		except IOError:
			return False		
		handle.close()
	
	print text,
	return True

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
		return False
				
	lines = f.readlines()
	f.close()
	
	blocks = []
	for i in range(len(lines)):
		header = re.split('\s+',lines[i])
		
		# a non-empty and non-comment line
		if( (header[0] != '') and (header[0][0] != '#') ):
		
			# create a new block with the header line
			blocks.append( {'type':header[0],'header':lines[i],'content':[],'l_start':i,'l_end':i} )
			
			# append all subsequent non-empty lines to the new block's content until an empty one appears
			for j in range(i +1,len(lines)):
				if(lines[j].strip() != ''):
					blocks[-1]['content'].append(lines[j])
					blocks[-1]['l_end'] = j
				else:
					break
					
			# increment the line read counters
			i = j
		
	return blocks
	
def mean_stdv(x):
	"""Calulate the mean and standard deviation from a list of numbers. Returns (mean,stdev)"""
	
	(n, mean, std) = (len(x), 0.0, 0.0)
	
	if( n == 1 ):
		return (x[0],0.0)
	
	for a in x:
		mean = mean + a
	mean = mean / float(n)

	for a in x:
		std = std + (a - mean)**2
	std = math.sqrt(std / float(n-1))

	return mean, std
