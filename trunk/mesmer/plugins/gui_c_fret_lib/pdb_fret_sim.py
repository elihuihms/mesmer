#!/usr/bin/env python

#
# E. Ihms - 2012.08.31
#
# Provided a PDB with FRET donor/acceptor pseudoatom positions, calculates a FRET P(r) and a decay curve
#

import sys
import argparse

from FRETSim import *

# parser block
parser = argparse.ArgumentParser()
parser.add_argument('-TDi', metavar='float', type=float, action='append', required=True, help='Donor lifetimes')
parser.add_argument('-TAi', metavar='float', type=float, action='append', required=True, help='Donor preexponentials')
parser.add_argument('-R0', metavar='float', type=float, default=55.0, required=True, help='FRET pair Forster distance')
parser.add_argument('-dR', metavar='float', type=float, default=5.0, required=True, help='FRET pair Forster distance uncertainty')
parser.add_argument('-QD', metavar='name', default='QD', required=True, help='Donor PDB pseudoatom name')
parser.add_argument('-QA', metavar='name', default='QA', required=True, help='Acceptor PDB pseudoatom name')
parser.add_argument('-pdb', metavar='FILE', default="input.pdb", required=True, help='The pdb containing donor/acceptor pseudoatoms.')
parser.add_argument('-irf', metavar='FILE', default="irf.dat", required=True, help='The file to output the fit to.')
parser.add_argument('-out', metavar='FILE', default="output.dat", required=True, help='The file to output the fit to.')
parser.add_argument('-fA', metavar='float', type=float, default=1.0, help='The fraction of acceptor sites actually labeled with an acceptor dye.')
parser.add_argument('-Pr', action='store_true', help='Print only the Pr() function and exit.')
parser.add_argument('-SkipChain', action='store_true', help='Skip acceptor fluorophores in the same chain as the donor.')
parser.add_argument('-SkipModel', action='store_true', help='Skip acceptor fluorophores in the same model as the donor.')
args = parser.parse_args()

# Read IRF
(irf_t,irf_I) = recfromtxt(args.irf,unpack=True)
Timepoints = list(irf_t)
IRF_values = list(irf_I)

# Read PDB
(Donors,Acceptors) = getPDBElements(args.pdb,args.QD,args.QA)

# calculate the distances between donors and acceptors
Distances = getPDBDistances(Donors,Acceptors,args.SkipChain,args.SkipModel)

if(len(Distances) == 0):
	print "No valid interatomic distances found for specified atom types '%s' and '%s'" % (args.QD,args.QA)
	exit(0)
	
# Write Pr() to file if requested
if(args.Pr):
	PDB_Pr = makePDBPr(Distances,args.dR)

	file = open( args.out, 'w' )
	for i in range(len(PDB_Pr)):
		file.write( "%i\t%.5f\n" % (i,PDB_Pr[i]) )
	file.close()
	
	sys.exit(0)
pass

file = open( args.out, 'w' )
for i in range(len(Timepoints)):
	file.write( "%0.5f\t%.5f\n" % (Timepoints[i],N_t(Timepoints[i],args.TDi,args.TAi,args.R0,Distances,args.dR,args.fA,(Timepoints,IRF_values))) )
file.close()
