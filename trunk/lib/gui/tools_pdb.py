import os
import tkMessageBox
import argparse
import Tkinter as tk
import tkFileDialog

from subprocess			import Popen,PIPE

from lib.gui.tools_plugin	import convertParserToOptions,makeListFromOptions
from lib.gui.win_options	import OptionsWindow

def makePDBs( w ):
	if(w.currentSelection[0] == None or w.currentSelection[1] == None):
		return

	tmp = []
	title = 'Choose folder containing component PDBs'
	while True:
		dir = tkFileDialog.askdirectory(title=title) #note - don't set parent, obscures the title
		if(not dir):
			break
		tmp.append(dir)
		title = 'Added %s. Select another?' % os.path.basename(dir)
	if(len(tmp)<1):
		return

	pdb_dirs = ' '.join(tmp)

	if( 'pdbOutput' not in w.pluginOptions ):
		parser = argparse.ArgumentParser()
		parser.add_argument('-Pmin',	type=float,		default=5,		metavar='5%',			help='Minimum prevalence for components to be included')
		parser.add_argument('-Wmin',	type=float,		default=0.05,	metavar='0.05',			help='Minimum weighting for components to be included')
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
	output = tkFileDialog.asksaveasfilename(title='Select name and location to save generation models:',initialfile=name,parent=w)
	if(not output):
		return

	if(os.path.exists(output) ):
		try:
			os.remove(output)
		except:
			tkMessageBox.showerror("Error","Could not remove existing PDB",parent=w)
			return

	tmp = makeListFromOptions( w.pluginOptions['pdbOutput'] ) # build the make_models argument string

	# does the user want to get just the best ensemble, or components from all ensembles?
	if w.pluginOptions['pdbOutput']['best']['value'] == 1:
		path = os.path.join(w.activeDir.get(), 'ensembles_%s_%05i.tbl' % (w.currentSelection[1],w.currentSelection[0]) )
		if( not os.access( path, os.R_OK ) ):
			tkMessageBox.showerror("Error","Could not read ensemble table \"%s\"" % path,parent=w)
			return
		tmp.extend( ['-ensembles',path] )
	else:
		path = os.path.join(w.activeDir.get(), 'component_statistics_%s_%05i.tbl' % (w.currentSelection[1],w.currentSelection[0]) )
		if( not os.access( path, os.R_OK ) ):
			tkMessageBox.showerror("Error","Could not read component statistics table \"%s\"" % path,parent=w)
			return
		tmp.extend( ['-stats',path] )

	cmd = [os.path.join(w.prefs['mesmer_util_path'],'make_models'),'-out',output,'-pdbs',pdb_dirs]
	cmd.extend( tmp )

	try:
		handle = Popen(cmd,stdout=PIPE,stderr=PIPE)
		handle.wait()
		if( handle.returncode != 0 ):
			tkMessageBox.showerror("Error","make_generation_models reported an error: %s" % handle.communicate()[0])
	except OSError as e:
		tkMessageBox.showerror("Error","Could not open make_generation_models: %s" % (e),parent=w)
		return
