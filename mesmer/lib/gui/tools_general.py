from multiprocessing import cpu_count

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
		
def getColumnNames( path ):
	handle = open(path)
	firstline = handle.readline()
	handle.close()
	
	ret = []
	if firstline[0] == "#" and len(firstline) > 3:
		return firstline[1:].rstrip().split()
	else:
		return None
		