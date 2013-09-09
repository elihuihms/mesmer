import subprocess

def getWhichPath( app ):
	proc = subprocess.Popen(["which",app], stdout=subprocess.PIPE)
	return proc.stdout.read().strip()
