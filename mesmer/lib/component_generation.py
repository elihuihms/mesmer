import glob
import os

from exceptions import *

def get_component_values( path ):
	try:
		f = open( path, 'r' )
	except IOError as e:
		raise ComponentGenException(e.msg)

	ret = {}
	for l in f.readlines():
		a = l.strip().split()

		# skip comments
		if(a[0][0] == '#'):
			continue

		if(a[0] != ''):
			if( a[0] in ret.keys() ):
				raise ComponentGenException( "ERROR: Already read values for component \"%s\"" % (a[0]) )
			ret[a[0]] = a

	f.close()

	return ret

def match_data_files( names, dirs ):
	"""
	Find the datafiles from the provided a list of directories matching the provided name
	"""

	ret = {}
	for n in names:
		ret[n] = []

	for d in dirs:
		for n in names:
			matches = glob.glob( "%s%s%s[._]*" % (d,os.sep,n) )

			if( len(matches) == 0 ):
				raise ComponentGenException("ERROR: Data file for component \"%s\" not found in directory \"%s\"" % (n,d))
			elif( len(matches) > 1 ):
				raise ComponentGenException("ERROR: Multiple data files for component \"%s\" found in directory \"%s\". E.g. \"%s\" and \"%s\"" % (n,d,matches[0],matches[1]))

			ret[n].append(matches[0])

	return ret

def write_component_files( data_vals, data_dirs, template, dir ):
	# create the component file
	for name in data_vals:
		new = template[:] # make a copy

		# replace all of the value fields first
		for (i,s) in enumerate(data_vals[name]):
			new = new.replace("%s%i" % ('$',i), s.strip() )

		# embed the datafiles
		for (i,f) in enumerate( data_dirs[name] ):

			try:
				handle = open( f, 'r' )
			except IOError:
				raise ComponentGenException("ERROR: Could not open component datafile \"%s\"" % (f))

			new = new.replace("%s%i" % ('%',i+1,), handle.read() )
			handle.close()

		# write the compiled datafile
		path = ("%s%s%s.component" % (dir,os.sep,name) )
		try:
			handle = open( path, 'w' )
		except IOError:
			raise ComponentGenException("ERROR: Could not write to component file \"%s\" " % (path))

		handle.write( new )
		handle.close()

	return True