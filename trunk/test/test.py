#!/usr/bin/env python

import os
import glob
import shutil
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-make_components',	action='store_true',	default=False )
parser.add_argument('-mesmer',			action='store_true',	default=False )
parser.add_argument('-all',				action='store_true',	default=False )

def run_process( cmd, path ):
	out = open( path, 'w' )
	handle = subprocess.Popen( cmd, stdout=out )
	handle.wait()
	out.close()

	if(handle.returncode > 0):
		print "\tError: %i - See %s" % (handle.returncode,path)
	else:
		print "\tSuccess"

	return handle

def test_make_components(path, args):
	print "Testing make_components..."
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
	print "Testing mesmer..."
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
