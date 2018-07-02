import os
import sys
import shutil
import tempfile
import tkFileDialog

from multiprocessing import cpu_count

def tryProgramCall( program, args=[] ):
	from subprocess	import Popen,PIPE
	from tempfile	import mkdtemp
	
	try:
		pHandle = Popen( [program]+args, cwd=mkdtemp(), stdout=PIPE, stderr=PIPE )
	except OSError as e:
		return False

	return True
		
def askNewDirectory(parent,**kwargs):
	# different options for creating a new directory
	
	path = tkFileDialog.asksaveasfilename(parent=parent,**kwargs)
	if path == '':
		return ''
		
	if os.path.exists(path):
		try:
			shutil.rmtree(path)
		except OSError as e:
			tkMessageBox.showerror("Error","Could not remove \"%s\": %s" %(path,e),parent=parent)
			return ''
	try:
		os.mkdir(path)
	except OSError as e:
		tkMessageBox.showerror("Error","Could not create \"%s\": %s" %(path,e),parent=parent)
		return ''
	
#	path = tkFileDialog.askdirectory(parent=parent,**kwargs)
#	if path == '':
#		return
#			
#	if os.listdir(path):
#		if tkMessageBox.askyesno('Warning',"Remove the existing folder \"%s\" and its contents?"%os.path.basename(path),parent=self):
#			try:
#				shutil.rmtree(path)
#				os.mkdir(args.dir)
#			except OSError as e:
#				tkMessageBox.showerror("Error","Could not replace the folder \"%s\": %s" %(path,e),parent=self)
#				return
#		else:
#			return
	return path
		
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
		