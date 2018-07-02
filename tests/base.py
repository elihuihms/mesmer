import unittest
import os
import sys
import shutil
import tempfile
import uuid
import logging

try:
	import mesmer
except ImportError:
	sys.path.append(os.path.abspath(".."))
	import mesmer

class TestBase(unittest.TestCase):
	def setUp(self):
		import mesmer.output
		mesmer.output._CONSOLE_OUTPUT = False
		mesmer.output._LOG_FILE_LEVEL = logging.DEBUG

		self.test_dir = tempfile.mkdtemp()
		self.init_dir = os.getcwd()
		self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"data"))

		os.chdir(self.test_dir)
		
	def tearDown(self,clean=True):
		if clean:
			shutil.rmtree(self.test_dir)
		else:
			print "Temporary file path: %s"%self.test_dir
		os.chdir(self.init_dir)
		
	def getFilePath(self,new=False):
		if new:
			self.test_file = os.path.join(self.test_dir,str(uuid.uuid4()))
		return self.test_file
	
	def getFileContents(self,path):
		with open(path, 'r') as content_file:
			return content_file.read()

class TestMESMER(TestBase):

	def test_output(self):
		import mesmer.setup
		import mesmer.output
		logs = mesmer.output.Logger()
		args = mesmer.setup.parse_arguments()
		args.dir = self.test_dir
		path = mesmer.output.open_results_dir( logs, args )
		test = os.path.join(self.test_dir,args.name)
		self.assertEqual(path, test)

	def test_failure(self):
		import mesmer.cli
		with self.assertRaises(SystemExit) as cm:
			mesmer.cli.run()
		self.assertEqual(cm.exception.code, 1)

	def test_mesmer(self):
		import mesmer.cli
		args = ["-dir",self.test_dir,'-ensembles','100','-Gmax','2']
		args.extend(["-target",os.path.join(self.data_dir,"test_cam_1.target")])
		args.extend(["-components",os.path.join(self.data_dir,"cam_components")])

		with self.assertRaises(SystemExit) as cm:
			mesmer.cli.run(args)

		self.assertEqual(cm.exception.code, 0)

#		print os.path.join(self.test_dir,"MESMER_Results",mesmer.output._LOG_FILE_TITLE)
		
#		self.assertIsNotNone(None)

		#self.assertTrue( os.path.isfile(os.path.join(self.test_dir,"base_1.png")) )

		#self.assertEqual( round(E.get_chisq(Q),1), 679.8 )

if __name__ == '__main__':
	unittest.main()