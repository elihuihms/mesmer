import os
import glob
import shutil
import tkMessageBox
import tkFileDialog

from subprocess import Popen, PIPE

class SAXSCalcException(Exception):
	def __init__(self,msg):
		self.msg = msg
	def __str__(self):
		return self.msg

def calcSAXSFromWindow( w ):
	dir = tkFileDialog.asksaveasfilename(title='New folder to save SAXS profiles:',parent=w,initialfile='saxs_profiles')
	if(dir == ''):
		return

	if(os.path.exists(dir)):
		shutil.rmtree(dir)
	try:
		os.mkdir(dir)
	except:
		tkMessageBox.showerror("SAXS Calculation Error","Could not create directory \"%s\"" % dir)
		return

	w.SAXSCalcAfterID = w.after( 1000, asyncCalcSAXS, *(w,dir) )
	return

def asyncCalcSAXS( w, dir ):
	i = w.SAXSCalcCounter.get()
	if( i >= len(w.pdbList) ):
		w.updateParent(dir)
		w.closeWindow()
		return

	try:
		calcSAXSProfile( w.SAXSCalcPath.get(), w.SAXSCalcArgs.get(), w.pdbList[i], dir )
	except SAXSCalcException as e:
		tkMessageBox.showerror("SAXS Calculation Error",e.msg)
		return

	w.SAXSCalcProgress.set("Progress: %i/%i" % (i+1,len(w.pdbList)) )
	w.SAXSCalcCounter.set(i+1)
	w.SAXSCalcAfterID = w.after( 1000, asyncCalcSAXS, *(w,dir) )

def calcSAXSProfile( prog, args, pdb, dir ):

	base = os.path.basename(pdb)
	name = os.path.splitext( os.path.basename(pdb) )[0]

	if not os.path.exists(pdb):
		raise SAXSCalcException( "Could not find \"%s\"" % (pdb) )

	try:
		shutil.copy(pdb,dir)
	except:
		raise SAXSCalcException( "Could not copy \"%s\" into directory \"%s\"" % (pdb,dir) )

	tmp = [prog]
	tmp.extend( args.split() )
	tmp.append( base )
	try:
		pipe = Popen(tmp, cwd=dir, stdout=PIPE)
	except:
		raise SAXSCalcException( "Could not find executable \"%s\"" % (prog) )

	pipe.wait()

	try:
		os.remove( "%s%s%s" % (dir,os.sep,base) )
	except:
		raise SAXSCalcException( "Could not remove temporary PDB \"%s\" from directory \%s\" " % (base,dir) )

	if( prog[-6:] == 'crysol' ):
		tmp = "%s%s%s00.int" % (dir,os.sep,name)
		if not os.path.exists(tmp):
			raise SAXSCalcException( "Failed to calculate SAXS profile for \"%s\". CRYSOL output: %s" % (pdb,pipe.stdout.read()) )

		try:
			lines = open( tmp ).readlines()[1:-1]
			f = open( "%s%s%s.dat" % (dir,os.sep,name), 'w' )
			for l in lines:
				f.write( "%s\n" % ("\t".join( l.split()[0:2] ) ) )
			f.close()
		except:
			raise SAXSCalcException( "Could not clean up CRYSOL profile \"%s\"" % (tmp) )

		os.remove("%s%s%s00.log" % (dir,os.sep,name) )
		os.remove("%s%s%s00.alm" % (dir,os.sep,name) )
		os.remove("%s%s%s00.int" % (dir,os.sep,name) )

	elif( prog[-4:] == 'foxs' ):
		tmp = "%s%s%s.dat" % (dir,os.sep,base)
		if not os.path.exists(tmp):
			raise SAXSCalcException( "Failed to calculate SAXS profile for \"%s\". FoXS output: %s" % (pdb,pipe.stdout.read()) )

		try:
			lines = open( tmp ).readlines()
			open( "%s%s%s.dat" % (dir,os.sep,name), 'w' ).writelines(lines[2:-1])
		except:
			raise SAXSCalcException( "Could not clean up FoXS profile \"%s\"" % (tmp) )

		os.remove("%s%s%s.dat" % (dir,os.sep,base) )
		os.remove("%s%s%s.plt" % (dir,os.sep,name) )
	else:
		tmp = glob.glob( "%s%s%s.*" % (dir,os.sep,name) )
		if( len(tmp) == 0 ):
			raise SAXSCalcException( "Failed to calculate SAXS profile for \"%s\". \"%s\" output: %s" % (pdb,prog,pipe.stdout.read()) )

	return True
