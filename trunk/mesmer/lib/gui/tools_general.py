def openUserPrefs( mode='r' ):
	import os.path
	import shelve

	home = os.path.expanduser("~")
	path = os.path.join( home, ".mesmer_prefs" )
	return shelve.open( path, mode )

def setDefaultPrefs( prefs ):
	import multiprocessing
	prefs['mesmer_base_dir'] = ''
	prefs['mesmer_scratch'] = ''
	prefs['cpu_count'] = multiprocessing.cpu_count()
	prefs['run_arguments'] = {'threads':prefs['cpu_count']}

def tryProgramCall( program ):
	from subprocess		import Popen,PIPE

	try:
		pHandle = Popen( program, stdout=PIPE, stderr=PIPE )
	except OSError as e:
		return False

	return True

