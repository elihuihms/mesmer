import os

def tests():
	def get_ensemble_stats(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','get_ensemble_stats.py'),
				os.path.join(paths[1],'cam_components_stats.tbl'),
				os.path.join(paths[1],'cam_mesmer_1','ensembles_test_cam_1_00000.tbl'),
				'-dCol',
				'1',
				'-avg',
				'-R'
			],[]
		)

	def make_attribute_plot(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_attribute_plot.py'),
				os.path.join(paths[1],'cam_components_stats.tbl'),
				'-spec',
				os.path.join(paths[1],'test_cam_1.spec'),
				'-stats',
				os.path.join(paths[1],'cam_mesmer_1','component_statistics_test_cam_1_00000.tbl'),
				'-ensembles',
				os.path.join(paths[1],'cam_mesmer_1','ensembles_test_cam_1_00000.tbl'),
				'-nogui',
				'-figure',
				os.path.join(paths[2],'cam_attr_plot_1.png')
			],[os.path.join(paths[2],'cam_attr_plot_1.png')]
		)

	def make_attribute_spec(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_attribute_spec.py'),
				os.path.join(paths[1],'cam_components_stats.tbl'),
				'-dCol',
				'1',
				'-mean',
				'32',
				'-stdev',
				'2',
				'-out',
				os.path.join(paths[2],'cam_spec_1.tbl')
			],[os.path.join(paths[2],'cam_spec_1.tbl')])

	def make_components(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_components.py'),
				'-template',
				os.path.join(paths[1],'test_cam_1.template'),
				'-values',
				os.path.join(paths[1],'test_cam_1.values'),
				'-data',
				os.path.join(paths[1],'cam_saxs'),
				os.path.join(paths[1],'cam_rdc_1'),
				os.path.join(paths[1],'cam_rdc_2'),
				os.path.join(paths[1],'cam_pcs_1'),
				os.path.join(paths[1],'cam_pcs_2'),
				'-out',
				os.path.join(paths[2],'cam_components')
			],[os.path.join(paths[2],'cam_components')])

	def make_curv_plot(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_curv_plot.py'),
				os.path.join(paths[1],'cam_mesmer_1','restraints_test_cam_1_SAXS_00000.out'),
				'-nogui',
				'-figure',
				os.path.join(paths[2],'cam_mesmer_1_CURV.png')
			],[os.path.join(paths[2],'cam_mesmer_1_CURV.png')]
		)

	def make_list_plot(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_list_plot.py'),
				os.path.join(paths[1],'cam_mesmer_1','restraints_test_cam_1_TABL1_00000.out'),
				os.path.join(paths[1],'cam_mesmer_1','restraints_test_cam_1_TABL2_00000.out'),
				'-xCol',
				'2',
				'-yCol',
				'3',
				'-nogui',
				'-figure',
				os.path.join(paths[2],'cam_mesmer_1_TABL.png')
			],[os.path.join(paths[2],'cam_mesmer_1_TABL.png')]
		)

	def make_saxs_plot(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_saxs_plot.py'),
				os.path.join(paths[1],'cam_mesmer_1','restraints_test_cam_1_SAXS_00000.out'),
				'-nogui',
				'-figure',
				os.path.join(paths[2],'cam_mesmer_1_SAXS.png')
			],[os.path.join(paths[2],'cam_mesmer_1_SAXS.png')]
		)

	def make_models_1(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_models.py'),
				os.path.join(paths[1],'cam_pdbs.tgz'),
				'-ensembles',
				os.path.join(paths[1],'cam_mesmer_1','ensembles_test_cam_1_00000.tbl'),
				'-out',
				os.path.join(paths[2],'cam_make_models_1.pdb'),
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],[os.path.join(paths[2],'cam_make_models_1.pdb')])

	def make_models_2(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_models.py'),
				os.path.join(paths[1],'cam_pdbs'),
				'-stats',
				os.path.join(paths[1],'cam_mesmer_1','component_statistics_test_cam_1_00000.tbl'),
				'-out',
				os.path.join(paths[2],'cam_make_models_2.pdb'),
				'-Pmin',
				'0',
				'-Wmin',
				'0'
			],[os.path.join(paths[2],'cam_make_models_2.pdb')])

	def make_synthetic_target(paths, args):
		return(
			[
				os.path.join(paths[0],'utilities','make_synthetic_target.py'),
				'-target',
				os.path.join(paths[1],'test_cam_1.target'),
				'-components',
				os.path.join(paths[1],'cam_components'),
				'-spec',
				os.path.join(paths[1],'test_cam_1.spec'),
				'-dir',
				paths[2]
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