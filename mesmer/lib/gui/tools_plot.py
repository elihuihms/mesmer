import os
import sys
import tkMessageBox
import argparse
import Tkinter as tk
import tkFileDialog

from subprocess		import Popen,PIPE

from mesmer.lib.exceptions import *
from mesmer.lib.ga_functions_output import _MESMER_CORRELATION_FILE_FORMAT,_MESMER_STATISTICS_FILE_FORMAT,_MESMER_RESTRAINTS_FILE_FORMAT
from mesmer.lib.plugin_functions import list_from_parser_dict

from mesmer.util.make_attribute_plot import MakeAttributePlot

from tools_general	import getColumnNames
from win_options	import OptionsWindow

def makeCorrelationPlot( w ):
	generation_count,target_name,data_type = w.currentSelection
	
	p1 = os.path.join(w.activeDir.get(), _MESMER_CORRELATION_FILE_FORMAT%generation_count )
	p2 = os.path.join(w.activeDir.get(), _MESMER_STATISTICS_FILE_FORMAT%(target_name,generation_count) )
	
	cmd = ['make_correlation_plot']
#	if( w.prefs['mesmer_base_dir'] != '' ):
#		cmd = [sys.executable,os.path.join(w.prefs['mesmer_base_dir'],'utilities','make_correlation_plot.py')]
	
	if( os.access( p1, os.R_OK ) and os.access( p2, os.R_OK ) ):
		cmd.extend( [p1,p2,'-size','20'] )
	elif( os.access( p1, os.R_OK ) ):
		tkMessageBox.showwarning("Warning","Component statistics not available, plotting only unweighted correlations",parent=w)
		cmd.extend( [p1,'-size','20'] )
	else:
		tkMessageBox.showerror("Error","Could not open generation correlation file \"%s\"" % p1,parent=w)
		return
				
	try:
		Popen(cmd)
	except Exception as e:
		tkMessageBox.showerror("Error","Could not open the correlation plot: %s" % (e),parent=w)
		return

def plotRestraint( w ):
	generation_count,target_name,data_type = w.currentSelection
	
	for p in w.plot_plugins:
		if (data_type in p.types):
			path = (os.path.join(w.activeDir.get(), _MESMER_RESTRAINTS_FILE_FORMAT%(target_name,data_type,generation_count)))

			if( not os.access( path, os.R_OK ) ):
				tkMessageBox.showerror("Error","Could not open the restraint file \"%s\"" % path ,parent=w)
				return

			if( p.parser ): # get options for the plugin
				if( p.name in w.pluginOptions ):
					options = w.pluginOptions[ p.name ]
				else:
					w.pluginOptions[ p.name ] = p.get_argument_dict()
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
					p.plot( path, w.pluginOptions[ p.name ], title="Best fit to %s %s data at generation %i"%(target_name,data_type,generation_count) )
				else:
					p.plot( path, None, title="Best fit to %s %s data at generation %i"%(target_name,data_type,generation_count) )
				return
			except (Exception,mesPluginError) as e:
				tkMessageBox.showerror("Error","Plotting plugin returned an error: %s" % (e))
	return
	
def plotAttributes( w ):
	p1 = w.attributeTable.get()
	if( not os.access( p1, os.R_OK ) ):
		tkMessageBox.showerror("Error","Could not read attribute table \"%s\"" % p1,parent=w)
		return
		
	column_names = getColumnNames( p1 )
	generation_count,target_name,data_type = w.currentSelection

	if(generation_count == None or target_name == None):
		return

	p2 = os.path.join(w.activeDir.get(), _MESMER_STATISTICS_FILE_FORMAT%(target_name,generation_count) )
	if( not os.access( p1, os.R_OK ) ):
		tkMessageBox.showerror("Error","Could not read component statistics table \"%s\"" % p2,parent=w)
		return

	plotter = MakeAttributePlot()
	w.pluginOptions['attributePlotter'] = plotter.get_argument_dict(tag="#GUI")
	print w.pluginOptions
		
	w.newWindow = tk.Toplevel(w.master)
	w.optWindow = OptionsWindow(w.newWindow, w.pluginOptions['attributePlotter'] )
	w.newWindow.focus_set()
	w.newWindow.grab_set()
	w.newWindow.transient(w)
	w.newWindow.wait_window()
	
	# convert column names into indices
	if column_names != None and len(column_names) > 2:
		for k,group in w.pluginOptions['attributePlotter'].iteritems():
			if group['dest'] == 'xCol':
				group['value'] = column_names.index(group['value'])
			elif group['dest'] == 'yCol':
				group['value'] = column_names.index(group['value'])
			elif group['dest'] == 'zCol' and group['value'] != '':
				group['value'] = column_names.index(group['value'])
		
	if w.optWindow.returncode == 0:
		cmd = ['make_attribute_plot']
		if( w.prefs['mesmer_base_dir'] != '' ):
			cmd = [sys.executable,os.path.join(w.prefs['mesmer_base_dir'],'utilities','make_attribute_plot.py')]
		cmd.extend( [p1,'-stats',p2] )
		cmd.extend( ['-title',"Attributes %s ensembles at generation %i"%(target_name,generation_count)] )
		cmd.extend( list_from_parser_dict( w.pluginOptions['attributePlotter'] ) )
		
		try:
			Popen(cmd)
		except OSError:
			tkMessageBox.showerror("Error","Could not open the attribute plotter",parent=w)
			return

def plotHistogram( w ):
	if( not w.resultsDB.has_key('ensemble_stats') ):
		return

	generation_count,target_name,data_type = w.currentSelection
	if(generation_count == None):
		return

	try:
		import pylab as P
	except:
		tkMessageBox.showerror("Error","Could not import matplotlib's pylab",parent=w)
		return

	n, bins, patches = P.hist(w.resultsDB['ensemble_stats'][generation_count]['scores'], 50, normed=1, histtype='stepfilled')
	P.setp(patches, 'facecolor', 'r', 'alpha', 0.75)
	P.show()

def plotScoreProgress( w ):
	if not w.resultsDB.has_key('ensemble_stats'):
		return

	try:
		import pylab as P
	except:
		tkMessageBox.showerror("Error","Could not import matplotlib's pylab",parent=w)
		return

	generations, best_scores, avg_scores, score_deviations = [],[],[],[]
	for (i,(scores,ratio,targets)) in enumerate(w.resultsDB['ensemble_stats']):
		generations.append( i )
		best_scores.append( scores[0] )
		avg_scores.append( scores[1] )
		score_deviations.append( scores[2] )

	P.plot( generations, avg_scores, lw=2, c='b' )
	P.errorbar( generations, avg_scores, yerr=score_deviations, fmt='o', c='b', label='Average' )
	P.plot( generations, best_scores, lw=2, c='r')
	P.scatter( generations, best_scores, label='Best', marker='o', c='r' )
	P.ion()
	P.show()

	return

