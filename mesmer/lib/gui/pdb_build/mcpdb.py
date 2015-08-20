#!/usr/bin/env python

import sys
import errno
import argparse
import copy

from random	import random
from mcpdb_objects	import *
from mcpdb_utilities	import *

parser = argparse.ArgumentParser()
parser.add_argument('-pdb', required=True)
parser.add_argument('-fixedDomain', nargs='+', default=[], action='append')
parser.add_argument('-rigidDomain', nargs='+', default=[], action='append')
parser.add_argument('-model', type=int, default=0)
parser.add_argument('-n', type=int, default=1)
parser.add_argument('-prefix', default='')
parser.add_argument('-clashMax', type=int, default=0)
parser.add_argument('-clashR', type=float, default=3.6)
parser.add_argument('-CA', action='store_true', default=False)
#parser.add_argument('-rama', action='store_true', default=False)

args = parser.parse_args()

fixed = []
for group in args.fixedDomain:
	fixed.append( [] )
	for specifier in group:
		try:
			fixed[-1].append( (specifier.split(':')[0], int(specifier.split(':')[1].split('-')[0]), int(specifier.split(':')[1].split('-')[1])) )
		except ValueError:
			print "Error interpreting \"%s\". Specification should be in the format chainid:startres-endres. E.g. A:5-10" % (' '.join(specifier))
			sys.exit( errno.EINVAL )

rigid = []
for group in args.rigidDomain:
	rigid.append( [] )
	for specifier in group:
		try:
			rigid[-1].append( (specifier.split(':')[0], int(specifier.split(':')[1].split('-')[0]), int(specifier.split(':')[1].split('-')[1])) )
		except ValueError:
			print "Error interpreting \"%s\". Specification should be in the format chainid:startres-endres. E.g. A:5-10" % (' '.join(specifier))
			sys.exit( errno.EINVAL )

err,msg = check_PDB( args.pdb, args.model )
if err > 0:
	print msg
	sys.exit( errno.EINVAL )

err,msg = check_groups( args.pdb, fixed+rigid, args.model )
if err > 0:
	print msg
	sys.exit( errno.EINVAL )

model = TransformationModel( args.pdb, fixed+rigid, args.model )

eval = ModelEvaluator( model, clash_radius=args.clashR, CA_only=args.CA, clash_cutoff=args.clashMax)

print "Initial clashes: %i" % (eval.count_clashes())

if args.prefix == '':
	args.prefix = "%s_"%(args.pdb.replace(".pdb",''))

linkers = model.get_linker_phipsi()
k,j = 0,0
while j < args.n:
	tmp = copy.deepcopy(linkers)	
	for l in tmp:
		for i in xrange(len(l)):
			l[i] = 2*3.14159*random(),2*3.14159*random()
	model.set_linker_phipsi( tmp )
	
	if eval.check():
		model.savePDB("%s%i.pdb"%j)
		j+=1
		print "Iteration %i SUCCESS" % (k)
	else:
		print "Iteration %i FAIL" % (k)
	
	k+=1

sys.exit( 0 )