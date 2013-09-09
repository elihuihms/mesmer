import os
import shutil
import Tkinter as tk
import tkMessageBox
import tkFileDialog

from datetime import datetime

from lib.component_generation import matchDataFiles,writeComponentFiles

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
		data_files = matchDataFiles( names, dirs )
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
		writeComponentFiles( names, data_files, template, tmp )
	except ComponentGenException as e:
		tkMessageBox.showerror("Error",e.msg,parent=w)
		return False

	tkMessageBox.showinfo("Success","%i component files were successfully written" % (len(names.keys())))
	return True
