#!/usr/bin/env python

import os
import sys
import glob
import shutil
import argparse
import subprocess

parser = argparse.ArgumentParser()

group0 = parser.add_argument_group('Core')
group0.add_argument('-mesmer',			action='store_true',	default=False )
group0.add_argument('-all',				action='store_true',	default=False )

group1 = parser.add_argument_group('Utilities')
group1.add_argument('-utilities',		action='store_true',	default=False )
group1.add_argument('-make_components',	action='store_true',	default=False )
group1.add_argument('-make_models',		action='store_true',	default=False )
group1.add_argument('-make_target',		action='store_true',	default=False )

def run_process( cmd, path, silent=False, resultFile=None ):
	out = open( path, 'w' )
	handle = subprocess.Popen( cmd, stdout=out )
	handle.wait()
	out.close()

	if(silent):
		return handle

	fail = False
	if(handle.returncode > 0):
		print "ERROR: %i\n                    See %s" % (handle.returncode,path)
		sys.stdout.flush()
		fail = True

	if resultFile and not os.path.exists(resultFile):
		print "ERROR: %i\n                    Expected output file \"%s\" not found. See %s" % (handle.returncode,resultFile,path)
		sys.stdout.flush()
		fail = True

	if not fail:
		print "PASS"
		sys.stdout.flush()

	return handle

def test_utilities(path, args):
	print "make_attribute_spec".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'utilities','make_attribute_spec'),
		os.path.join(path,'data','cam_components_stats.tbl'),
		'-dCol',
		'0',
		'-mean',
		'32',
		'-stdev',
		'2',
		'-out',
		os.path.join(path,'out','cam_spec_1.tbl')
	]
	run_process( cmd, os.path.join(path,'out','cam_make_attribute_spec.txt'), resultFile=cmd[-1] )



def test_make_components(path, args):
	print "make_components".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'utilities','make_components'),
		'-template',
		os.path.join(path,'data','test_cam_1.template'),
		'-values',
		os.path.join(path,'data','test_cam_1.values'),
		'-data',
		os.path.join(path,'data','cam_saxs'),
		os.path.join(path,'data','cam_rdc_1'),
		os.path.join(path,'data','cam_rdc_2'),
		os.path.join(path,'data','cam_pcs_1'),
		os.path.join(path,'data','cam_pcs_2'),
		'-out',
		os.path.join(path,'out','cam_components')
	]

	run_process( cmd, os.path.join(path,'out','cam_components.txt') )

def test_mesmer(path, args):
	print "mesmer".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'mesmer'),
		'-dir',
		os.path.join(path,'out'),
		'-name',
		'cam_mesmer_1',
		'-target',
		os.path.join(path,'data','test_cam_1.target'),
		'-components',
		os.path.join(path,'data','cam_components'),
		'-size',
		'1',
		'-ensembles',
		'1000',
		'-Gmax',
		'0',
		'-Pbest',
		'-Popt',
		'-Pextra',
		'-Pstate'
	]

	run_process( cmd, os.path.join(path,'out','cam_mesmer_1.txt') )
	return

def test_make_models(path, args):
	print "make_models 1/2".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'utilities','make_models'),
		'-ensembles',
		'data/cam_mesmer_1/ensembles_test_cam_1_00000.tbl',
		'-pdb',
		'data/cam_pdbs.tgz',
		'-out',
		'out/cam_make_models_1.pdb',
		'-Pmin',
		'0',
		'-Wmin',
		'0'
	]
	run_process( cmd, os.path.join(path,'out','cam_make_models_1.txt') )

	print "make_models 2/2".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'utilities','make_models'),
		'-stats',
		'data/cam_mesmer_1/component_statistics_test_cam_1_00000.tbl',
		'-pdb',
		'data/cam_pdbs',
		'-out',
		'out/cam_make_models_2.pdb',
		'-Pmin',
		'0',
		'-Wmin',
		'0'
	]
	run_process( cmd, os.path.join(path,'out','cam_make_models_2.txt') )
	return

def test_make_synthetic_target(path, args):
	print "make_synthetic_target".ljust(40),
	sys.stdout.flush()
	cmd = [
		os.path.join(os.path.dirname(path),'utilities','make_synthetic_target'),
		'-target',
		os.path.join(path,'data','test_cam_1.target'),
		'-components',
		os.path.join(path,'data','cam_components'),
		'-spec',
		os.path.join(path,'data','test_cam_1.spec'),
		'-dir',
		os.path.join(path,'out')
	]
	run_process( cmd, os.path.join(path,'out','cam_make_target.txt'), resultFile=os.path.join(path,'out','restraints_test_cam_1_SAXS_00000.out') )
	return

if(__name__ == "__main__"):
	path	= os.path.dirname(os.path.abspath(__file__))
	args	= parser.parse_args()

	try:
		shutil.rmtree( os.path.join(path,'out') )
	except:
		pass
	os.mkdir( os.path.join(path,'out') )

	if(args.make_components or args.all):
		test_make_components( path, args )

	if(args.mesmer or args.all):
		test_mesmer( path, args )

	if(args.make_models or args.utilities or args.all):
		test_make_models(path, args)

	if(args.make_target or args.utilities or args.all):
		test_make_synthetic_target(path, args)
