import scipy

def get_ensembles_from_state( path, unique=False ):
	"""
	Returns a dict with ensemble info loaded from a MESMER ensemble state file
	"""

	f = open( path )

	header = f.readline()
	M = ( len(header.split()) -3) / 2 # size of ensembles

	targets = {}
	for (i,line) in enumerate(f.readlines()):

		# split out the ensemble weights and components for each target
		a = line.split()
		if(len(a) == 2*M +3):

			if( a[M+1] not in targets ):
				targets[ a[M+1] ] = []

			targets[ a[M+1] ].append( {
				'fitness'	:float(a[M+2]),
				'components':a[1:M+1],
				'weights'	:map(float,a[M+3:])
				} )

	if( not unique ):
		return targets

	N = len( targets[targets.keys()[0]] ) #number of ensembles

	ret = {}
	for t in targets:

		ensemble_sets = []
		ensemble_counts = []
		ensemble_fitnesses = []
		ensemble_weights = []

		for i in range(N):
			test_set = set(targets[t][i]['components'])

			# sort the component weights consistently by component name
			o = scipy.argsort( targets[t][i]['components'] )
			w = scipy.take(targets[t][i]['weights'],o)

			try:
				index = ensemble_sets.index( test_set )
			except ValueError:
				ensemble_sets.append( test_set )
				ensemble_counts.append( 1 )
				ensemble_fitnesses.append( targets[t][i]['fitness'] )
				ensemble_weights.append( w )
				continue

			ensemble_counts[ index ] += 1
			ensemble_fitnesses[ index ] += targets[t][i]['fitness']
			for j in range(M):
				ensemble_weights[ index ][j] += w[j]

		ret[ t ] = []
		for i in range(len(ensemble_sets)):
			avg_fitness = ensemble_fitnesses[i] / ensemble_counts[i]
			avg_weights = ensemble_weights[i] / ensemble_counts[i]
			ret[ t ].append( {'fitness':avg_fitness,'components':list(ensemble_sets[i]),'weights':avg_weights,'count':ensemble_counts[i]} )

	return ret