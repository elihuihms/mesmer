import math

def mean_stdv(x):
	"""Calulate the mean and standard deviation from a list of numbers. Returns (mean,stdev)"""

	(n, mean, std) = (len(x), 0.0, 0.0)

	if( n == 1 ):
		return (x[0],0.0)

	for a in x:
		mean = mean + a
	mean = mean / float(n)

	for a in x:
		std = std + (a - mean)**2
	std = math.sqrt(std / float(n-1))

	return mean, std

def extract_list_elements( l, k ):
	""" Returns a new list containing only the specified indexes"""
	new = []
	for i in k:
		new.append(l[i])
	return new

def map_2d( l, func ):
	for i in range(len(l)):
		l[i] = map( func, l[i] )
	return l