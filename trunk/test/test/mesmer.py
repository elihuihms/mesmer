import os

def tests():

	def mesmer(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer.py'),
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
			],
			None
		)

	return [
		('mesmer',mesmer)
	]