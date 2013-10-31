import os
import tkMessageBox
import argparse
import Tkinter as tk
import tkFileDialog

from subprocess			import Popen,PIPE

from lib.gui.tools_plugin	import convertParserToOptions,makeListFromOptions
from lib.gui.win_options	import OptionsWindow

def makeCorrelationPlot( w ):
	p1 = os.path.join(w.activeDir.get(), 'component_correlations_%05i.tbl' % w.currentSelection[0] )
	p2 = os.path.join(w.activeDir.get(), 'component_statistics_%s_%05i.tbl' % (w.currentSelection[1],w.currentSelection[0]) )
	if( os.access( p1, os.R_OK ) and os.access( p2, os.R_OK ) ):
		cmd = os.path.join(w.prefs['mesmer_util_path'],'make_correlation_plot')
		try:
			Popen([cmd,p1,p2,'-size','20'])
		except Exception as e:
			tkMessageBox.showerror("Error","Could not open the correlation plot: %s" % (e),parent=w)
			return
	elif( os.access( p1, os.R_OK ) ):
		tkMessageBox.showwarning("Warning","Component statistics not available, plotting only unweighted correlations",parent=w)
		cmd = os.path.join(w.prefs['mesmer_util_path'],'make_correlation_plot')
		try:
			Popen([cmd,p1,'-size','20'])
		except Exception as e:
			tkMessageBox.showerror("Error","Could not open correlation plot: %s" % (e),parent=w)
			return
	else:
		tkMessageBox.showerror("Error","Could not open generation correlation file \"%s\"" % p1,parent=w)

def plotRestraint( w ):
	for p in w.plot_plugins:
		if (w.currentSelection[2] in p.types):

			path = (os.path.join(w.activeDir.get(), 'restraints_%s_%s_%05i.out' % (w.currentSelection[1],w.currentSelection[2],w.currentSelection[0])))

			if( not os.access( path, os.R_OK ) ):
				tkMessageBox.showerror("Error","Could not open the restraint file \"%s\"" % path ,parent=w)
				return

			if( p.parser ): # get options for the plugin
				if( p.name in w.pluginOptions ):
					options = w.pluginOptions[ p.name ]
				else:
					w.pluginOptions[ p.name ] = convertParserToOptions( p.parser )
				w.optWindowMaster = tk.Toplevel(w.master)
				w.optWindow = OptionsWindow(w.optWindowMaster, w.pluginOptions[ p.name ] )
				w.optWindowMaster.focus_set()
				w.optWindowMaster.grab_set()
				w.optWindowMaster.transient(w)
				w.optWindowMaster.wait_window(w.optWindowMaster)
				if w.optWindow.returncode != 0:
					return

			try:
				if( p.parser ):
					p.plot( path, w.pluginOptions[ p.name ] )
				else:
					p.plot( path )
				return
			except Exception as e:
				tkMessageBox.showerror("Error","Plotting plugin experienced an error: %s" % (e))

def plotAttributes( w ):
	p1 = w.attributeTable.get()
	if( not os.access( p1, os.R_OK ) ):
		tkMessageBox.showerror("Error","Could not read attribute table \"%s\"" % p1,parent=w)
		return

	if(w.currentSelection[0] == None or w.currentSelection[1] == None):
		return

	p2 = os.path.join(w.activeDir.get(), 'component_statistics_%s_%05i.tbl' % (w.currentSelection[1],w.currentSelection[0]) )
	if( not os.access( p1, os.R_OK ) ):
		tkMessageBox.showerror("Error","Could not read component statistics table \"%s\"" % p2,parent=w)
		return

	if( 'attributePlotter' not in w.pluginOptions ):
		parser = argparse.ArgumentParser()
		parser.add_argument('-nCol',	type=int,	default=0,		help='Column containing component names')
		parser.add_argument('-xCol',	type=int,	default=1,		help='Column to use as the plot\'s X axis')
		parser.add_argument('-yCol',	type=int,	default=2,		help='Column to use as the plot\'s Y axis')
		parser.add_argument('-axes',				default='',		help='Axes sizing (Xmin Xmax Ymin Ymax)')
		parser.add_argument('-xLabel',				default='',		help='The label for the x-axis')
		parser.add_argument('-yLabel',				default='',		help='The label for the y-axis')
		parser.add_argument('-statNorm',	action='store_true', 	help='Normalize variable color saturation for component prevalence')
		parser.add_argument('-statSame',	action='store_true',	help='Do not use variable color saturation for component prevalence')
		parser.add_argument('-statWeight',			type=float, default='',		help='When plotting MESMER statistics, drop components weighted lower than this amount')
		parser.add_argument('-statPrevalence',		type=float,	default='',		help='When plotting MESMER statistics, drop components with prevalences lower than this amount')
		parser.add_argument('-statSubsample',		type=float,	default='',		help='Randomly subsample selected conformers by a percentage.')
		w.pluginOptions['attributePlotter'] = convertParserToOptions( parser )

	w.newWindow = tk.Toplevel(w.master)
	w.optWindow = OptionsWindow(w.newWindow, w.pluginOptions['attributePlotter'] )
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	w.newWindow.transient(w)
	w.newWindow.wait_window()
	if w.optWindow.returncode == 0:
		p.plot( path, w.pluginOptions[ p.name ] )

	cmd = [os.path.join(w.prefs['mesmer_util_path'],'make_attribute_plot'),p1,'-stats',p2]
	cmd.extend( makeListFromOptions( w.pluginOptions['attributePlotter'] ) )
	try:
		Popen(cmd)
	except OSError:
		tkMessageBox.showerror("Error","Could not open the attribute plotter",parent=w)
		return

def plotHistogram( w ):
	if( not w.resultsDB.has_key('ensemble_stats') ):
		return

	if(w.currentSelection[0] == None):
		return

	try:
		import pylab as P
	except:
		tkMessageBox.showerror("Error","Could not import matplotlib's pylab",parent=w)
		return

	#n, bins, patches = P.hist(w.resultsDB['ensemble_stats'][w.currentSelection[0]]['scores'], 50, normed=1, histtype='stepfilled')
	#P.setp(patches, 'facecolor', 'r', 'alpha', 0.75)
	#P.show()

def makePDBs( w ):
	if(w.currentSelection[0] == None or w.currentSelection[1] == None):
		return

	p1 = os.path.join(w.activeDir.get(), 'component_statistics_%s_%05i.tbl' % (w.currentSelection[1],w.currentSelection[0]) )
	if( not os.access( p1, os.R_OK ) ):
		tkMessageBox.showerror("Error","Could not read component statistics table \"%s\"" % p2,parent=w)
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
		parser.add_argument('-Pmin',	type=float,				default=5,		metavar='5%',							help='Minimum prevalence for components to be included')
		parser.add_argument('-Wmin',	type=float,				default=0.05,	metavar='0.05',							help='Minimum weighting for components to be included')
		w.pluginOptions['pdbOutput'] = convertParserToOptions( parser )

	w.newWindow = tk.Toplevel(w.master)
	w.optWindow = OptionsWindow(w.newWindow, w.pluginOptions['pdbOutput'] )
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	w.newWindow.transient(w)
	w.newWindow.wait_window()
	if w.optWindow.returncode == 0:
		p.plot( path, w.pluginOptions[ p.name ] )

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

	cmd = [os.path.join(w.prefs['mesmer_util_path'],'make_generation_models'),p1,'-wAttr','-out',output,'-pdbs',pdb_dirs]
	cmd.extend( makeListFromOptions( w.pluginOptions['pdbOutput'] ) )

	try:
		handle = Popen(cmd,stdout=PIPE,stderr=PIPE)
		handle.wait()
		if( handle.returncode != 0 ):
			tkMessageBox.showerror("Error","make_generation_models reported an error: %s" % handle.communicate()[0])
	except OSError as e:
		tkMessageBox.showerror("Error","Could not open make_generation_models: %s" % (e),parent=w)
		return


