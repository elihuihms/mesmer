from multiprocessing import cpu_count

def openUserPrefs( mode='r' ):
	import os.path
	import shelve

	home = os.path.expanduser("~")
	path = os.path.join( home, ".mesmer_prefs" )
	return shelve.open( path, mode )

def setDefaultPrefs( shelf ):
	import multiprocessing
	shelf['mesmer_base_dir'] = ''
	shelf['mesmer_scratch'] = ''
	shelf['cpu_count'] = cpu_count()
	shelf['run_arguments'] = {'threads':shelf['cpu_count']}
	shelf['disabled_plugins'] = []
	shelf['plugin_prefs'] = {}

def tryProgramCall( program ):
	from subprocess		import Popen,PIPE

	try:
		pHandle = Popen( program, stdout=PIPE, stderr=PIPE )
	except OSError as e:
		return False

	return True

def revealDirectory( dir ):
	from subprocess import call
	from sys import platform
	
	if platform == 'darwin':
		call( ['open',dir] )
	elif platform == 'linux2':
		call( ['xdg-open',dir] )
	elif platform == 'win32':
		call( ['explorer',dir] )
	else:
		print "Unrecognized platform %s"%(platform)