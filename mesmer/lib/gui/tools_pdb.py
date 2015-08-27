import os
import sys
import tkMessageBox
import argparse
import Tkinter as tk
import tkFileDialog

from subprocess		import Popen,PIPE

from .. ga_functions_output import _MESMER_ENSEMBLES_FILE_FORMAT,_MESMER_CORRELATION_FILE_FORMAT,_MESMER_STATISTICS_FILE_FORMAT,_MESMER_RESTRAINTS_FILE_FORMAT

from tools_general	import askNewDirectory
from tools_plugin	import convertParserToOptions,makeListFromOptions
from win_options	import OptionsWindow

def makePDBs( w ):
	if(w.currentSelection[0] == None or w.currentSelection[1] == None):
		return

	pdb_dirs = []
	title = 'Choose folder containing component PDBs'
	while True:
		path = tkFileDialog.askdirectory(title=title,initialdir=w.prefs['last_open_dir'],mustexist=True) #note - don't set parent, obscures the title in OSX
		if(not path):
			break
		w.prefs['last_open_dir'] = os.path.dirname(path)
		pdb_dirs.append(path)
		title = 'Added %s. Select another?' % os.path.basename(path)
	if(len(pdb_dirs)<1):
		return

	if( 'pdbOutput' not in w.pluginOptions ):
		parser = argparse.ArgumentParser()
		parser.add_argument('-Pmin',	metavar="Minimum Prevalence",	type=float,		default=5,		help='Minimum prevalence for components to be included')
		parser.add_argument('-Wmin',	metavar="Minimum Weighting",	type=float,		default=0.05,	help='Minimum weighting for components to be included')
		parser.add_argument('-wAttr',	action='store_true',			default=False,			help='Write UCSF Chimera attribute files?')
		parser.add_argument('-wPyMol',	action='store_true',			default=False,			help='Write PyMol coloration scripts?')
		parser.add_argument('-best',	action='store_true',			default=False,			help='Save only the best ensemble?')
		w.pluginOptions['pdbOutput'] = convertParserToOptions( parser )

	w.newWindow = tk.Toplevel(w.master)
	w.optWindow = OptionsWindow(w.newWindow, w.pluginOptions['pdbOutput'] )
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	w.newWindow.transient(w)
	w.newWindow.wait_window()
	if w.optWindow.returncode != 0:
		return

	name = "%05i_models.pdb" % w.currentSelection[0]
	output = askNewDirectory(w,title='Select location to save generation models:',initialfile=name,initialdir=w.prefs['last_open_dir'])
	if(not output):
		return
	w.prefs['last_open_dir'] = os.path.dirname(output)

	if( w.prefs['mesmer_base_dir'] == '' ):
		cmd = ['make_models']
	else:
		cmd = [sys.executable,os.path.join(w.prefs['mesmer_base_dir'],'utilities','make_models.py')]
	
	cmd.extend(pdb_dirs) # append collected PDB sources
	cmd.extend( makeListFromOptions(w.pluginOptions['pdbOutput']) ) # build the make_models argument string

	# does the user want to get just the best ensemble, or components from all ensembles?
	if w.pluginOptions['pdbOutput']['best']['value'] == 1:
		path = os.path.join(w.activeDir.get(), _MESMER_ENSEMBLES_FILE_FORMAT%(w.currentSelection[1],w.currentSelection[0]) )
		if( not os.access( path, os.R_OK ) ):
			tkMessageBox.showerror("Error","Could not read ensemble table \"%s\"" % path,parent=w)
			return
		cmd.extend( ['-ensembles',path] )
	else:
		path = os.path.join(w.activeDir.get(), _MESMER_STATISTICS_FILE_FORMAT%(w.currentSelection[1],w.currentSelection[0]) )
		if( not os.access( path, os.R_OK ) ):
			tkMessageBox.showerror("Error","Could not read component statistics table \"%s\"" % path,parent=w)
			return
		cmd.extend( ['-stats',path] )

	cmd.extend(['-out',output])

	try:
		handle = Popen(cmd,stdout=PIPE,stderr=PIPE)
		handle.wait()
		if( handle.returncode != 0 ):
			tkMessageBox.showerror("Error","make_generation_models reported an error: %s" % (''.join(handle.communicate())) )
	except OSError as e:
		tkMessageBox.showerror("Error","Could not open make_generation_models: %s" % (e),parent=w)
		return
