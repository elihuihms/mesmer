import scipy
import copy

def get_ensembles_from_state( path, unique=False ):
	"""
	Returns a list with ensemble info loaded from a MESMER ensemble state file
	"""

	f = open( path )

	header = f.readline()
	M = ( len(header.split()) -2) / 2 # size of ensembles

	ensembles = []
	for (i,line) in enumerate(f.readlines()):

		# split out the ensemble weights and components
		a = line.split()
		if(len(a) == 2*M +2):

			ensembles.append( {
				'fitness'	:float(a[M+1]),
				'components':a[1:M+1],
				'weights'	:map(float,a[M+2:])
				} )

	if( not unique ): # if we're just reading the ensemble list, return now
		return ensembles

	ensemble_sets = []
	ensemble_counts = []
	ensemble_fitnesses = []
	ensemble_weights = []

	for e in ensembles:
		test_set = set(e['components'])

		# sort the component weights consistently by component name
		o = scipy.argsort( e['components'] )
		w = scipy.take(e['weights'],o)

		try:
			index = ensemble_sets.index( test_set )
		except ValueError:
			ensemble_sets.append( test_set )
			ensemble_counts.append( 1 )
			ensemble_fitnesses.append( e['fitness'] )
			ensemble_weights.append( w )
			continue

		ensemble_counts[ index ] += 1
		ensemble_fitnesses[ index ] += e['fitness']
		for j in range(M):
			ensemble_weights[ index ][j] += w[j]

	ret = []
	for i in range(len(ensemble_sets)):
		avg_fitness = ensemble_fitnesses[i] / ensemble_counts[i]
		avg_weights = ensemble_weights[i] / ensemble_counts[i]
		ret.append( {'fitness':avg_fitness,'components':list(ensemble_sets[i]),'weights':avg_weights,'count':ensemble_counts[i]} )

	return ret