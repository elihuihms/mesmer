import os

def tests():

	def mesmer( paths, args):
		return(
			[
				os.path.join(paths[0],'mesmer.py'),
				'-threads',
				'3',
				'-dir',
				paths[2],
				'-name',
				'cam_mesmer_1',
				'-target',
				os.path.join(paths[1],'test_cam_1.target'),
				'-components',
				os.path.join(paths[1],'cam_components'),
				'-size',
				'3',
				'-ensembles',
				'1000',
				'-Gmax',
				'3',
				'-Pbest',
				'-Popt',
				'-Pextra',
				'-Pstate'
			],[]
		)

	return [
		('mesmer',mesmer)
	]