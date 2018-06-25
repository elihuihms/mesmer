import os
import glob
import shelve
import Tkinter as tk
import tkMessageBox
import tkFileDialog

from mesmer.lib.setup_functions		import *
from mesmer.lib.plugin_functions	import load_plugins

from tools_TkTooltip		import ToolTip
from tools_general			import revealDirectory
from tools_plugin			import getPluginPrefs,setPluginPrefs

class PluginWindow(tk.Frame):
	def __init__(self, master=None):
		self.master = master
		self.master.title('Plugin Manager')
		
		self.master.resizable(width=False, height=False)
		self.master.protocol('WM_DELETE_WINDOW', self.close)

		tk.Frame.__init__(self,master)
		self.pack(expand=True,fill='both',padx=6,pady=6)
		self.pack_propagate(True)

		self.loadPrefs()
		self.createWidgets()
		self.loadPlugins()
		self.setWidgetState()

	def loadPrefs(self):
		try:
			self.prefs = open_user_prefs()
		except Exception as e:
			tkMessageBox.showerror("Error",'Cannot read MESMER preferences file: %s' % (e),parent=self)
			self.master.destroy()		

	def close(self):
		self.master.destroy()

	def createWidgets(self):	
		self.f_tools = tk.Frame(self,borderwidth=0,width=450)
		self.f_tools.grid(column=0,row=0,sticky=tk.E+tk.W)
		self.addPluginButton = tk.Button(self.f_tools,text='Add...',command=lambda:revealDirectory(os.path.join(self.prefs['mesmer_base_dir'],'plugins')))
		self.addPluginButton.grid(column=0,row=0,sticky=tk.W)
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

		self.pluginListIndex		= tk.IntVar()
		self.plugin_list_checkboxes	= []
		self.plugin_list_checkstate	= []
		self.plugin_list_ids		= []
		self.plugin_list_types		= []
		self.plugin_list_versions	= []
		self.plugin_info		= []

		self.plugin_ids				= []
		self.plugin_states			= [] # -1,0,1 = error,disabled,enabled
		self.plugin_modules			= []

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

	def createPluginRow(self, container, id, module, error, disabled ):		
		if container == self.f_mesmerplugins:
			row = self.mesmerplugins_count
			self.mesmerplugins_count +=1
		elif container == self.f_calcplugins:
			row = self.calcplugins_count
			self.calcplugins_count +=1
		elif container == self.f_plotplugins:
			row = self.plotplugins_count
			self.plotplugins_count +=1
		
		if error:
			type,version = '',''
			state = tk.DISABLED
		elif disabled:
			type,version = module.types[0],module.version
			state = tk.DISABLED
		else:
			type,version = module.types[0],module.version
			state = tk.NORMAL
		
		rowcount = (self.mesmerplugins_count + self.calcplugins_count + self.plotplugins_count) -1
		self.plugin_list_checkboxes.append( tk.Radiobutton(container,variable=self.pluginListIndex,value=rowcount,command=self.setWidgetState) )
		self.plugin_list_checkboxes[-1].grid(column=0,row=row, sticky=tk.W)
		self.plugin_list_ids.append( tk.Label(container, text=id, state=state, width=20) )
		self.plugin_list_ids[-1].grid(column=1,row=row, sticky=tk.W)
		self.plugin_list_types.append( tk.Label(container, text=type, state=state, width=6) )
		self.plugin_list_types[-1].grid(column=2,row=row, sticky=tk.E)
		self.plugin_list_versions.append( tk.Label(container, text=version, state=state, width=20) )
		self.plugin_list_versions[-1].grid(column=3,row=row, sticky=tk.E)
		
	def togglePluginRow( self, index, enable ):
		state = tk.DISABLED
		if enable:
			state = tk.NORMAL
		self.plugin_list_ids[ index ].configure(state=state)
		self.plugin_list_types[ index ].configure(state=state)
		self.plugin_list_versions[ index ].configure(state=state)
		self.setWidgetState()
	
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
		
		self.pluginInfoText.insert(1.0, self.plugin_info[index] )
		if self.plugin_states[index] == 1: # -1,0,1 = error,disabled,enabled
			self.disablePluginButton.configure(state=tk.NORMAL)
		elif self.plugin_states[index] == 0:
			self.enablePluginButton.configure(state=tk.NORMAL)

		if self.plugin_modules[index] != None and self.plugin_modules[index].path != None:
			savedpath = getPluginPrefs( self.prefs, self.plugin_modules[index].name )['path']
			if savedpath == None:
				self.pluginExecutablePath.set( self.plugin_modules[index].path )
			else:
				self.pluginExecutablePath.set( savedpath )
				
			self.pluginExecutableLabel.configure(state=tk.NORMAL)
			self.pluginExecutableEntry.configure(state=tk.NORMAL)
			self.pluginExecutableButton.configure(state=tk.NORMAL)
		else:
			self.pluginExecutablePath.set( '' )
		
	def disablePlugin(self,id=None):
		if id == None:
			index = int(self.pluginListIndex.get())
			id = self.plugin_ids[index]
		else:
			index = None
		tmp = self.prefs['disabled_plugins']
		tmp.append(id)
		self.prefs['disabled_plugins'] = list(set(tmp))
		self.prefs.sync()
		if index != None:
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
		if self.plugin_modules[index].path[-1] == os.sep:
			self.pluginExecutablePath.set( tkFileDialog.askdirectory(title='Select directory for this plugin:',mustexist=True,parent=self) )
		else:
			self.pluginExecutablePath.set( tkFileDialog.askopenfilename(title='Select executable for this plugin:',parent=self) )
		self.pluginApplyButton.configure(state=tk.NORMAL)

	def enableApplyButton(self, evt):
		self.pluginApplyButton.configure(state=tk.NORMAL)		
		
	def applyPluginSettings(self, evt):
		index,newpath = int(self.pluginListIndex.get()),self.pluginExecutablePath.get()

		if newpath != self.plugin_modules[index].path:
			if newpath == '': # reset
				setPluginPrefs( self.prefs, self.plugin_modules[index].name, path=None )
				self.pluginExecutablePath.set( self.plugin_modules[index].path )
			else:
				setPluginPrefs( self.prefs, self.plugin_modules[index].name, path=newpath)
			
		self.pluginApplyButton.configure(state=tk.DISABLED)	
	
	def loadPlugins(self):
		mesmer_path = set_module_paths()

		def _apply( id, ok, msg, module, container ):
			self.plugin_ids.append( id )

			if ok:
				disabled = id in self.prefs['disabled_plugins']

				self.plugin_modules.append( module )
				self.plugin_states.append( not disabled )
				self.plugin_info.append( module.info )
				self.createPluginRow( container, id, module=module, error=False, disabled=disabled )
			else:
				self.disablePlugin(id) # force disabling of broken plugins
				
				self.plugin_modules.append(None)
				self.plugin_states.append( -1 )
				self.plugin_info.append( msg )
				self.createPluginRow( container, id, module=None, error=True, disabled=None )

		for id,ok,msg,module in load_plugins( mesmer_path, 'mesmer', args=parse_arguments([],self.prefs) ):
			_apply(id,ok,msg,module,self.f_mesmerplugins)

		for id,ok,msg,module in load_plugins( mesmer_path, 'gui_c' ):
			_apply(id,ok,msg,module,self.f_calcplugins)
					
		for id,ok,msg,module in load_plugins( mesmer_path, 'gui_p' ):
			_apply(id,ok,msg,module,self.f_plotplugins)
