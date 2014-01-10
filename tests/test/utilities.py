import os

def tests():
	def get_ensemble_stats(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','get_ensemble_stats.py'),
				os.path.join(path,'data','cam_components_stats.tbl'),
				os.path.join(path,'data','cam_mesmer_1','ensembles_test_cam_1_00000.tbl'),
				'-dCol',
				'1',
				'-avg',
				'-R'
			],[]
		)
	
	def make_attribute_plot(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_attribute_plot.py'),
				os.path.join(path,'data','cam_components_stats.tbl'),
				'-spec',
				os.path.join(path,'data','test_cam_1.spec'),
				'-stats',
				os.path.join(path,'data','cam_mesmer_1','component_statistics_test_cam_1_00000.tbl'),
				'-ensembles',
				os.path.join(path,'data','cam_mesmer_1','ensembles_test_cam_1_00000.tbl'),
				'-nogui',
				'-figure',
				os.path.join(path,'out','cam_attr_plot_1.png')
			],[os.path.join(path,'out','cam_attr_plot_1.png')]
		)		
				
	def make_attribute_spec(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_attribute_spec.py'),
				os.path.join(path,'data','cam_components_stats.tbl'),
				'-dCol',
				'1',
				'-mean',
				'32',
				'-stdev',
				'2',
				'-out',
				os.path.join(path,'out','cam_spec_1.tbl')
			],[os.path.join(path,'out','cam_spec_1.tbl')])

	def make_components(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_components.py'),
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
			],[os.path.join(path,'out','cam_components')])		

	def make_curv_plot(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_curv_plot.py'),
				os.path.join(path,'data','cam_mesmer_1','restraints_test_cam_1_SAXS_00000.out'),
				'-nogui',
				'-figure',
				os.path.join(path,'out','cam_mesmer_1_CURV.png')
			],[os.path.join(path,'out','cam_mesmer_1_CURV.png')]
		)
	
	def make_list_plot(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_list_plot.py'),
				os.path.join(path,'data','cam_mesmer_1','restraints_test_cam_1_TABL1_00000.out'),
				os.path.join(path,'data','cam_mesmer_1','restraints_test_cam_1_TABL2_00000.out'),
				'-xCol',
				'2',
				'-yCol',
				'3',
				'-nogui',
				'-figure',
				os.path.join(path,'out','cam_mesmer_1_TABL.png')
			],[os.path.join(path,'out','cam_mesmer_1_TABL.png')]
		)
	
	def make_saxs_plot(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_saxs_plot.py'),
				os.path.join(path,'data','cam_mesmer_1','restraints_test_cam_1_SAXS_00000.out'),
				'-nogui',
				'-figure',
				os.path.join(path,'out','cam_mesmer_1_SAXS.png')
			],[os.path.join(path,'out','cam_mesmer_1_SAXS.png')]
		)
		
	def make_models_1(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_models.py'),
				'data/cam_pdbs.tgz',
				'-ensembles',
				'data/cam_mesmer_1/ensembles_test_cam_1_00000.tbl',
				'-out',
				'out/cam_make_models_1.pdb',
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],[os.path.join(path,'out','cam_make_models_1.pdb')])
	
	def make_models_2(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_models.py'),
				'data/cam_pdbs',
				'-stats',
				'data/cam_mesmer_1/component_statistics_test_cam_1_00000.tbl',
				'-out',
				'out/cam_make_models_2.pdb',
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],[os.path.join(path,'out','cam_make_models_2.pdb')])

	def make_synthetic_target(path, args):
		return(
			[
				os.path.join(os.path.dirname(path),'mesmer','utilities','make_synthetic_target.py'),
				'-target',
				os.path.join(path,'data','test_cam_1.target'),
				'-components',
				os.path.join(path,'data','cam_components'),
				'-spec',
				os.path.join(path,'data','test_cam_1.spec'),
				'-dir',
				os.path.join(path,'out')
			],[])
			
	return[
		('get_ensemble_stats',get_ensemble_stats),
		('make_attribute_plot',make_attribute_plot),
		('make_attribute_spec',make_attribute_spec),
		('make_components',make_components),
		('make_curv_plot',make_curv_plot),
		('make_list_plot',make_list_plot),
		('make_saxs_plot',make_saxs_plot),
		('make_models 1/2',make_models_1),
		('make_models 2/2',make_models_2),
		('make_synthetic_target',make_synthetic_target)
	]