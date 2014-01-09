import subprocess
import sys
import os

def run_test( name, test, path, args=[], silent=False ):
	print name.ljust(40),
	sys.stdout.flush()

	# get the cmd generator function and result file (if any)
	(cmd,resultFile) = test(path, args)

	log_path = "%s%sout%s%s_out.txt" % (path,os.sep,os.sep,name.replace(os.sep,'') )
	log = open( log_path, 'w' )
	handle = subprocess.Popen( cmd, stdout=log )
	handle.wait()
	log.close()

	if(silent):
		return handle

	fail = False
	if(handle.returncode > 0):
		print "FAIL: %i\n                    See %s" % (handle.returncode,log_path)
		sys.stdout.flush()
		fail = True

	if resultFile and not os.path.exists(resultFile):
		print "FAIL: %i\n                    Expected output file \"%s\" not found. See %s" % (handle.returncode,resultFile,log_path)
		sys.stdout.flush()
		fail = True

	if not fail:
		print "PASS"
		sys.stdout.flush()

	return handle