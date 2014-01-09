import os

def tests():
	def make_components(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'utilities','make_components.py'),
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
			],os.path.join(path,'out','cam_components'))		

	def make_models_1(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'utilities','make_models.py'),
				'data/cam_pdbs.tgz',
				'-ensembles',
				'data/cam_mesmer_1/ensembles_test_cam_1_00000.tbl',
				'-out',
				'out/cam_make_models_1.pdb',
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],os.path.join(path,'out','cam_make_models_1.pdb'))
	
	def make_models_2(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'utilities','make_models.py'),
				'data/cam_pdbs',
				'-stats',
				'data/cam_mesmer_1/component_statistics_test_cam_1_00000.tbl',
				'-out',
				'out/cam_make_models_2.pdb',
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],os.path.join(path,'out','cam_make_models_2.pdb'))

	def make_synthetic_target(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'utilities','make_synthetic_target.py'),
				'-target',
				os.path.join(path,'data','test_cam_1.target'),
				'-components',
				os.path.join(path,'data','cam_components'),
				'-spec',
				os.path.join(path,'data','test_cam_1.spec'),
				'-dir',
				os.path.join(path,'out')
			],None)
				
	def make_attribute_spec(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'utilities','make_attribute_spec.py'),
				os.path.join(path,'data','cam_components_stats.tbl'),
				'-dCol',
				'1',
				'-mean',
				'32',
				'-stdev',
				'2',
				'-out',
				os.path.join(path,'out','cam_spec_1.tbl')
			],None)
			
	return[
		('make_components',make_components),
		('make_models 1/2',make_models_1),
		('make_models 2/2',make_models_2),
		('make_synthetic_target',make_synthetic_target),
		('make_attribute_spec',make_attribute_spec)
	]