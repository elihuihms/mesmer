import os
import glob
import shelve
import Tkinter as tk
import tkMessageBox
import tkFileDialog

from .. plugin_functions	import load_plugins
from .. setup_functions		import parse_arguments,open_user_prefs

from tools_TkTooltip		import ToolTip
from tools_general			import revealDirectory
from tools_plugin			import getPluginPrefs,setPluginPrefs

class PluginWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.geometry('450x360+100+100')
		self.master.title('Plugin Manager')
		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master,width=450,height=360)
		self.grid()
		self.grid_propagate(0)

		self.loadPrefs()
		self.createWidgets()
		self.loadPlugins()
		self.setWidgetState()

	def loadPrefs(self):
		try:
			self.prefs = open_user_prefs(mode='w')
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()		

	def close(self):
		self.master.destroy()

	def createWidgets(self):	
		self.f_tools = tk.Frame(self,borderwidth=0,width=450)
		self.f_tools.grid(column=0,row=0,sticky=tk.E+tk.W)
		self.addPluginButton = tk.Button(self.f_tools,text='Add...',command=self.revealPluginDirectory)
		self.addPluginButton.grid(column=0,row=0,sticky=tk.W)
		#self.delPluginButton = tk.Button(self.f_tools,text='Remove Plugin',state=tk.DISABLED)
		#self.delPluginButton.grid(column=1,row=0,sticky=tk.W)
		self.enablePluginButton = tk.Button(self.f_tools,text='Enable',state=tk.DISABLED,command=self.enablePlugin)
		self.enablePluginButton.grid(column=1,row=0,sticky=tk.E)
		self.disablePluginButton = tk.Button(self.f_tools,text='Disable',state=tk.DISABLED,command=self.disablePlugin)
		self.disablePluginButton.grid(column=2,row=0,sticky=tk.E)
	
		self.f_mesmerplugins	= tk.LabelFrame(self,width=450,text='Attribute comparison plugins')
		self.f_mesmerplugins.grid(column=0,row=1,sticky=tk.E+tk.W,padx=8)
		self.mesmerplugins_count	= 0

		self.f_calcplugins		= tk.LabelFrame(self,width=450,text='Attribute calculation plugins')
		self.f_calcplugins.grid(column=0,row=2,sticky=tk.E+tk.W,padx=8)
		self.calcplugins_count	= 0

		self.f_plotplugins		= tk.LabelFrame(self,width=450,text='Attribute plotting plugins')
		self.f_plotplugins.grid(column=0,row=3,sticky=tk.E+tk.W,padx=8)
		self.plotplugins_count	= 0

		self.rowcount = 0
		self.pluginListIndex		= tk.IntVar()
		self.plugin_list_checkboxes	= []
		self.plugin_list_checkstate	= []
		self.plugin_list_ids		= []
		self.plugin_list_types		= []
		self.plugin_list_versions	= []
		self.plugin_list_info		= []

		self.plugin_ids				= []
		self.plugin_names			= []
		self.plugin_states			= []

		self.f_actions = tk.LabelFrame(self,width=450,text='Plugin information')
		self.f_actions.grid(column=0,row=4,sticky=tk.E+tk.W,padx=8)
		self.pluginInfoText = tk.Text(self.f_actions,width=56,height=6,wrap=tk.WORD)
		self.pluginInfoText.grid(column=0,columnspan=4,row=0,sticky=tk.E)
		self.pluginExecutableLabel = tk.Label(self.f_actions, text='Executable path:', state=tk.DISABLED)
		self.pluginExecutableLabel.grid(column=0,row=1,sticky=tk.W)
		self.pluginExecutablePath = tk.StringVar()
		self.pluginExecutableEntry = tk.Entry(self.f_actions,width=26,textvariable=self.pluginExecutablePath,state=tk.DISABLED)
		self.pluginExecutableEntry.bind('<KeyRelease>', self.enableApplyButton)
		self.pluginExecutableEntry.grid(column=1,row=1,sticky=tk.E+tk.W)
		self.pluginExecutableButton = tk.Button(self.f_actions,text='Set...',state=tk.DISABLED)
		self.pluginExecutableButton.bind('<ButtonRelease-1>',self.setPluginPath)
		self.pluginExecutableButton.grid(column=2,row=1,sticky=tk.E)
		self.pluginApplyButton = tk.Button(self.f_actions,text='Apply',state=tk.DISABLED)
		self.pluginApplyButton.grid(column=2,row=2,sticky=tk.E)
		self.pluginApplyButton.bind('<ButtonRelease-1>',self.applyPluginSettings)

		self.f_footer = tk.Frame(self,width=450,borderwidth=0)
		self.f_footer.grid(column=0,row=5)
		self.closeButton = tk.Button(self.f_footer,text='Close',command=self.close)
		self.closeButton.grid(column=0,row=0,sticky=tk.E)

	def createPluginRow(self, container, error, id, type, version ):		
		if container == self.f_mesmerplugins:
			row = self.mesmerplugins_count
			self.mesmerplugins_count +=1
		elif container == self.f_calcplugins:
			row = self.calcplugins_count
			self.calcplugins_count +=1
		elif container == self.f_plotplugins:
			row = self.plotplugins_count
			self.plotplugins_count +=1
		self.plugin_ids.append( id )

		try:
			disabled = id in self.prefs['disabled_plugins']
		except KeyError:
			disabled = False
		
		if error:
			self.plugin_states.append( -1 ) # -1 = error on load
			state = tk.DISABLED
		elif disabled:
			self.plugin_states.append( 0 ) # 0 = disabled
			state = tk.DISABLED
		else:
			self.plugin_states.append( 1 ) # enabled
			state = tk.NORMAL
		
		self.plugin_list_checkboxes.append( tk.Radiobutton(container,variable=self.pluginListIndex,value=self.rowcount,command=self.setWidgetState) )
		self.plugin_list_checkboxes[-1].grid(column=0,row=row, sticky=tk.W)
		self.plugin_list_ids.append( tk.Label(container, text=id, state=state, width=20) )
		self.plugin_list_ids[-1].grid(column=1,row=row, sticky=tk.W)
		self.plugin_list_types.append( tk.Label(container, text=type, state=state, width=6) )
		self.plugin_list_types[-1].grid(column=2,row=row, sticky=tk.E)
		self.plugin_list_versions.append( tk.Label(container, text=version, state=state, width=20) )
		self.plugin_list_versions[-1].grid(column=3,row=row, sticky=tk.E)

		self.master.geometry('450x%i' % (360+self.rowcount*20))
		self.config(width=450,height=(360+self.rowcount*20))
		self.rowcount += 1

	def togglePluginRow( self, index, enable ):
		state = tk.DISABLED
		if enable:
			state = tk.NORMAL
		self.plugin_list_ids[ index ].configure(state=state)
		self.plugin_list_types[ index ].configure(state=state)
		self.plugin_list_versions[ index ].configure(state=state)
		self.setWidgetState()
	
#	def destroyPluginRow(self,index):
#		self.plugin_list_checkboxes[index].destroy()
#		del self.plugin_list_checkstate[index]
#		self.plugin_list_ids[index].destroy()
#		self.plugin_list_states[index].destroy()
#		self.plugin_list_versions[index].destroy()
#		
#		self.rowcount -=1
#		if(self.rowCounter==0):
#			self.delRowButton.config(state=tk.DISABLED)
#
#		self.master.geometry('450x%i' % (360+self.rowcount*30))
#		self.config(width=450,height=(360+self.rowcount*30))
	
	def setWidgetState(self):
		index = int(self.pluginListIndex.get())
		id = self.plugin_ids[ index ]
		self.pluginInfoText.delete(1.0,tk.END)
		self.enablePluginButton.configure(state=tk.DISABLED)
		self.disablePluginButton.configure(state=tk.DISABLED)
		self.pluginExecutableLabel.configure(state=tk.DISABLED)
		self.pluginExecutableEntry.configure(state=tk.DISABLED)
		self.pluginExecutableButton.configure(state=tk.DISABLED)
		self.pluginApplyButton.configure(state=tk.DISABLED)		
		
		self.pluginInfoText.insert(1.0, self.plugin_list_info[index] )
		if self.plugin_states[index] == 1: # -1,0,1 = error,disabled,enabled
			self.disablePluginButton.configure(state=tk.NORMAL)
		elif self.plugin_states[index] == 0:
			self.enablePluginButton.configure(state=tk.NORMAL)
		path = getPluginPrefs( self.prefs, self.plugin_names[index] )['path']
		if path != None:
			self.pluginExecutablePath.set( path )
		else:
			self.pluginExecutablePath.set( '' )
		if path != None and self.plugin_states[index] > 0:
			self.pluginExecutableLabel.configure(state=tk.NORMAL)
			self.pluginExecutableEntry.configure(state=tk.NORMAL)
			self.pluginExecutableButton.configure(state=tk.NORMAL)

		
	def disablePlugin(self):
		index = int(self.pluginListIndex.get())
		tmp = self.prefs['disabled_plugins']
		tmp.append(self.plugin_ids[index])
		self.prefs['disabled_plugins'] = list(set(tmp))
		self.prefs.sync()
		self.plugin_states[index] = 0
		self.togglePluginRow( index, False )
		self.setWidgetState()

	def enablePlugin(self):
		index = int(self.pluginListIndex.get())
		tmp = self.prefs['disabled_plugins']
		tmp.remove(self.plugin_ids[index])
		self.prefs['disabled_plugins'] = tmp
		self.prefs.sync()
		self.plugin_states[index] = 1
		self.togglePluginRow( index, True )
		self.setWidgetState()
			
	def setPluginPath(self, evt):
		index = int(self.pluginListIndex.get())
		if getPluginPrefs( self.prefs, self.plugin_names[index] )['path'][-1] == os.sep:
			tmp = tkFileDialog.askdirectory(title='Select directory for this plugin:',mustexist=True,parent=self)
		else:
			tmp = tkFileDialog.askopenfilename(title='Select executable for this plugin:',parent=self)
		if(tmp == ''):
			return
		self.pluginExecutablePath.set(tmp)
		self.pluginApplyButton.configure(state=tk.NORMAL)

	def enableApplyButton(self, evt):
		self.pluginApplyButton.configure(state=tk.NORMAL)		
		
	def applyPluginSettings(self, evt):
		index = int(self.pluginListIndex.get())
		setPluginPrefs( self.prefs, self.plugin_names[index], path=str(self.pluginExecutablePath.get()) )
		self.pluginApplyButton.configure(state=tk.DISABLED)	
	
	def revealPluginDirectory(self):
		revealDirectory( os.path.join(self.prefs['mesmer_base_dir'],'plugins') )

	def loadPlugins(self):
		def _apply( id, ok, msg, module, container ):
			if ok:
				if type(module.type) == str:
					datatype = module.type
				else:
					datatype = module.type[0]
					
				self.plugin_names.append( module.name )
				self.plugin_list_info.append( module.info )
				self.createPluginRow( container, False, id, datatype, module.version )
				if getPluginPrefs( self.prefs, module.name )['path'] == None: setPluginPrefs( self.prefs, id, path=module.path )
			else:
				self.plugin_names.append(None)
				self.plugin_list_info.append( error )
				self.createPluginRow( self.f_mesmerplugins, True, id, '', '' )

		for (id,ok,msg,module) in load_plugins( self.prefs['mesmer_base_dir'], 'mesmer', dry_run=True, args=parse_arguments('') ):
			_apply(id,ok,msg,module,self.f_mesmerplugins)

		for (id,ok,msg,module) in load_plugins( self.prefs['mesmer_base_dir'], 'gui_c', dry_run=True ):
			_apply(id,ok,msg,module,self.f_calcplugins)
					
		for (id,ok,msg,module) in load_plugins( self.prefs['mesmer_base_dir'], 'gui_p', dry_run=True ):
			_apply(id,ok,msg,module,self.f_plotplugins)
