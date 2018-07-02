	# set run arguments from preferences
	if prefs != None:
		for action in [a.__dict__ for a in parser.__dict__['_actions']]:
			name,value,default = action['dest'],getattr(ret,action['dest'],None),action['default']
			if value == None:
				continue
			if value == default and name in prefs['run_arguments']:
#				print "INFO:\tOverwriting argument \"-%s\" default to \"%s\" based on user preferences."%(name,prefs['run_arguments'][name])
				setattr(ret, name, prefs['run_arguments'][name])


	def _set_ensemble_state(self, ensembles):

		try:
			f = open( args.resume, 'r' )
		except IOError:
			print_msg( "\t\tERROR:\tCould not open ensemble state table \"%s\"" % file )
			return False

		names = components.keys()

		i = 0
		for line in f:
			if(i>len(ensembles)):
				print_msg( "\t\tWARNING:\tStopped loading ensemble state file at table %i" % (i+1) )
				break

			# read only the first target (components are the same, only weights different)
			a = line.split()
			if(len(a) != (2*args.size)+4):
				print_msg( "\t\tINFO:\tFinished reading ensemble state table (%i ensembles loaded)" % (i+1) )
				break

			for j in range(args.size):
				if(not a[j +1] in names):
					print_msg( "\t\tERROR:\tComponent \"%s\" referenced in line %i of ensemble state table not found in loaded components" % (a[j+1],i+1) )
				else:
					ensembles[i].component_names[j] = a[j+1]

			i+=1

		f.close()
		return True