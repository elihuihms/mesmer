from random import gauss

# Reference: James C. Spall, Handbook of Computational Statistics (2004), pgs 177-178
# see: http://www.jhuapl.edu/spsa/PDF-SPSA/Handbook04_StochasticOptimization.pdf
# also http://fedc.wiwi.hu-berlin.de/xplore/ebooks/html/csa/node51.html

def blind_random_min( fitFunc, startVec, stdDev, maxIter, allowNeg=False ):
	"""
	Minimizes the fitFunc function return value by blind stochastic modification of its input vector
	See James C. Spall, Handbook of Computational Statistics (2004), pgs 177-178
	
	Returns the optimized vector.
	
	Arguments:
	fitFunc		- The function to be minimized, must take a single input vector (list) and return a single float value
	startVec	- List, the starting coefficient vector
	stdDev		- Float, the gaussian standard dev. to be used in the creation of the perturbation vector
	maxIter		- Integer, the number of iterations to optimize the function over
	allowNeg	- Boolean, are negative perturbation vector components allowed?
	"""

	vecSize = len(startVec)
	
	# currVec is the vector that we will perturb
	currVec = startVec[:]
	
	bestScore = fitFunc( currVec )
	
	for i in range( maxIter ):
		# make a copy of our old vector
		oldVec = currVec[:]
	
		# modify our current vector by a gaussian random
		for j in range( vecSize ):
			currVec[ j ] = gauss(currVec[ j ], stdDev)
			
			if (currVec[ j ] < 0) and (not allowNeg):
				currVec[ j ] = 0.0
		
		# see if our new vector has minimized our loss function
		testScore = fitFunc( currVec )
		
		if (testScore < bestScore):
			bestScore = testScore
		else: # if we've not improved, reset
			newVec = oldVec[:]
			
	return newVec
			
def localized_random_min( fitFunc, startVec, stdDev, maxIter, allowNeg=False ):
	"""
	Minimizes the fitFunc function return value by a localized stochastic modification of its input vector
	See James C. Spall, Handbook of Computational Statistics (2004), pgs 177-178
	
	Returns the optimized vector.
	
	Arguments:
	fitFunc		- The function to be minimized, must take a single input vector (list) and return a single float value
	startVec	- List, the starting coefficient vector
	stdDev		- Float, the gaussian standard dev. to be used in the creation of the perturbation vector
	maxIter		- Integer, the number of iterations to optimize the function over
	allowNeg	- Boolean, are negative perturbation vector components allowed?
	"""
	
	vecSize = len(startVec)
	
	pertVec = [0.0] * vecSize
	currVec = startVec[:]

	bestScore = fitFunc( currVec )
	
	def vec_add( vec1, vec2 ):
		vecOut = vec1[:]
		for i in range(len(vec1)):
			vecOut[ i ] += vec2[ i ]
		return vecOut
	
	for i in range( maxIter ):
				
		# add our current vector to our existing oe
		newVec = vec_add( currVec, pertVec )
		
		for j in range( vecSize ):
			if (newVec[ j ] < 0) and (not allowNeg):
				newVec[ j ] = 0.0
		
		# see if the function value for the perturbed vector is smaller than our previous attempt
		testScore = fitFunc( newVec )
		if ( testScore < bestScore ):
			currVec = newVec
			bestScore = testScore
		else: # our perturbation vector is no good, get rid of it
			for j in range(vecSize):
				pertVec[j] = gauss(0, stdDev)
					
	return currVec
