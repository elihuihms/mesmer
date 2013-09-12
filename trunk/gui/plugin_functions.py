import inspect

def convertParserToDict( parser ):
	"""
	This is a very horrible function.
	It returns descriptive dictionary of arguments from an argparse parser by inspecting the parser._actions dictionary of functions and extracting their arguments.
	"""

	savetypes = ['help','option_strings','choices','type','dest','default','choices','required']

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
