import os
import shutil
import Tkinter as tk
import tkMessageBox
import tkFileDialog

from datetime import datetime

from .. exceptions				import *
from .. component_generation	import *
from .. plugin_functions		import *
from win_options				import *
from win_status					import *
from tools_plugin				import *
from tools_multiprocessing		import PluginParallelizer

_PDB_calculator_timer = 500 # in ms

def makeComponentsFromWindow( w ):
	paths = w.componentPDBsList.get(0,tk.END)

	names = {}
	for p in paths:
		n = os.path.splitext(os.path.basename(p))[0]
		names[n] = [n]

	dirs = []
	type_counters = {}
	template = """# autogenerated by mesmer-gui
# %s

NAME	$0

""" % (datetime.now())
	for i in range(w.rowCounter):
		dirs.append( w.widgetRowFolders[i].get() )
		type	= w.widgetRowTypes[i].get()
		if(type in type_counters):
			type_counters[type]+=1
		else:
			type_counters[type]=0

		template+="%s%i\n%%%i\n\n" % (type,type_counters[type],i+1)

	try:
		data_files = match_data_files( names, dirs )
	except ComponentGenException as e:
		tkMessageBox.showerror("Error",e.msg,parent=w)
		return False

	tmp = tkFileDialog.asksaveasfilename(title='Save components folder:',parent=w,initialfile='components')
	if(tmp == ''):
		return False
	if(os.path.exists(tmp)):
		shutil.rmtree(tmp)

	try:
		os.mkdir(tmp)
	except OSError:
		tkMessageBox.showerror("Error","ERROR: Couldn't create component folder.",parent=w)
		return False

	try:
		write_component_files( names, data_files, template, tmp )
	except ComponentGenException as e:
		tkMessageBox.showerror("Error",e.msg,parent=w)
		return False

	tkMessageBox.showinfo("Success","%i component files were successfully written" % (len(names.keys())))
	return True

def calcDataFromWindow( w, pdbs, pluginName ):

	# find the plugin matching the provided name
	plugin = None
	for p in w.calc_plugins:
		if( p.name == pluginName ):
			plugin = p
	if(plugin == None):
		return

	# overwrite plugin executable path
	if getPluginPrefs( w.prefs, plugin.name )['path'] != None:
		plugin.path = getPluginPrefs( w.prefs, plugin.name )['path']

	# get user-specifiable options from the plugin argument parser object
	options = convertParserToOptions( plugin.parser )
	
	# retrieve saved options from preferences
	saved_options = getPluginPrefs( w.prefs, plugin.name )['options']
	for o in options:
		if o['dest'] in saved_options and saved_options[o['dest']] != None: o['value'] = saved_options[o['dest']]


	# open the options window to set plugin variables
	w.newWindow = tk.Toplevel(w.master)
	w.optWindow = OptionsWindow(w.newWindow,options)
	w.newWindow.transient(w)
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	w.newWindow.wait_window()
	if w.optWindow.returncode > 0: # did user cancel the options window?
		return
	
	# save the modified preferences/options with a handy generator	
	setPluginPrefs( w.prefs, plugin.name, options={o['dest']:o['value'] for o in options} )

#	path = tkFileDialog.askdirectory(title="Directory to save calculated data to:",parent=w)
	path = tkFileDialog.asksaveasfilename(title='Directory to save calculated data to:',parent=w, initialfile="%s_data" % (plugin.type) )
	if(path == ''):
		return
	if(os.path.exists(path)):
		shutil.rmtree(path)
	try:
		os.mkdir(path)
	except:
		tkMessageBox.showerror("Error","Could not create folder \"%s\"" % path,parent=w)
		return
	
	try:
		ok = plugin.setup( w, options, path )
	except Exception as e:
		tkMessageBox.showerror("Error","Plugin reported a problem: %s" % (e),parent=w)
		return		
	if not ok:
		return

	# update the parent window row
	for i in range(w.rowCounter):
		if( w.widgetRowTypes[i].get() == plugin.type and w.widgetRowFolders[i].get() == '' ):
			w.widgetRowFolders[i].set( path )
			break

	# initialize the calculator
	w.Calculator = PluginParallelizer(plugin,threads=w.prefs['cpu_count'])
	w.Calculator.put(pdbs)
	w.counter = 0
	
	# open the status window
	w.newWindow = tk.Toplevel(w.master)
	w.statWindow = StatusWindow(w.newWindow,w.Calculator.abort,plugin.name)
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	
	w.Calculator.AfterID = w.after( _PDB_calculator_timer, calculatorStatus, w, pdbs )

	return w.newWindow
		
def calculatorStatus( w, pdbs ):
	for error,(pdb,info) in w.Calculator.get():
		w.counter += 1
		if error:
			w.Calculator.abort()
			tkMessageBox.showerror("Error","Encountered an error while processing PDB \"%s\":\n\n%s" % (pdb,info),parent=w)
			w.statWindow.close()
			return	

	if( w.counter == len(pdbs) ):
		w.Calculator.stop()
		w.statWindow.master.destroy()
	else:
		w.statWindow.CalcProgress.set("Progress: %i/%i" % (w.counter+1,len(pdbs)) )
		w.statWindow.CurrentPDB.set( os.path.basename( pdbs[w.counter] ) )
		w.AfterID = w.after( _PDB_calculator_timer, calculatorStatus, w, pdbs )
