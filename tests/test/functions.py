import subprocess
import sys
import os

def run_test( name, test, paths, args=[], silent=False ):
	"""
	Calls the "test" function argument to generate a command list, and runs the returned command.
	After the called command exits, checks for generated files (if requested) and notifies the user about the status of the call.
	"""

	# tell the user what test we are running
	print name.ljust(40),
	sys.stdout.flush()

	# get the cmd generator function and result file (if any)
	(cmd,files) = test(paths, args)

	log_path = os.path.join(paths[2],"%s_out.txt" % (name.replace(os.sep,'')) )
	log = open( log_path, 'w' )
	handle = subprocess.Popen( cmd, stdout=log )
	handle.wait()
	log.close()

	# no checking
	if(silent):
		return handle

	fail = False
	if(handle.returncode > 0):
		print "FAIL: %i\n                    See %s" % (handle.returncode,log_path)
		sys.stdout.flush()
		fail = True

	for file in files:
		if not os.path.exists(file):
			print "FAIL: %i\n                    Expected output file \"%s\" not found. See %s" % (handle.returncode,os.path.basename(file),os.path.basename(log_path))
			sys.stdout.flush()
			fail = True
			break

	if not fail:
		print "PASS"
		sys.stdout.flush()

	return handle