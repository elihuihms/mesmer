import subprocess

def getWhichPath( app ):
	proc = subprocess.Popen(["which",app], stdout=subprocess.PIPE)
	proc.wait()
	return proc.stdout.read().strip()
