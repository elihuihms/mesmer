import os
import sys

if sys.version_info < (2, 6, 0):
	sys.stderr.write("MESMER requires Python 2.6 or newer.\n")
	sys.exit(-1)

from setuptools import setup,find_packages

EXCLUDE_FROM_PACKAGES = []

mesmer = __import__('mesmer')
setup(
	name				= 'MESMER',
	version				= mesmer.__version__,
	license				= mesmer.__license__,
	author				= mesmer.__author__,
	author_email		= mesmer.__author_email__,
	description			= mesmer.__description__,
	url					= mesmer.__url__,
	download_url		= mesmer.__download_url__,
	platforms			= 'any',
		
	install_requires = [
		'matplotlib>=1.3',
		'numpy>=1.3',
		'scipy>=0.11',
		'biopython>=1.6',
	],

	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
	],
	
	packages = find_packages(exclude=EXCLUDE_FROM_PACKAGES),
	include_package_data = True,
	
	entry_points = {
		'console_scripts': [
			'mesmer = mesmer.mesmer_cli:run',
			'mesmer-gui = mesmer.mesmer_gui:run',
			'get_ensemble_stats = mesmer.utilities.get_ensemble_stats:run',
			'make_attribute_plot = mesmer.utilities.make_attribute_plot:run',
			'make_attribute_spec = mesmer.utilities.make_attribute_spec:run',
			'make_components = mesmer.utilities.make_components:run',
			'make_correlation_plot = mesmer.utilities.make_correlation_plot:run',
			'make_curv_plot = mesmer.utilities.make_curv_plot:run',
			'make_list_plot = mesmer.utilities.make_list_plot:run',
			'make_models = mesmer.utilities.make_models:run',
			'make_saxs_plot = mesmer.utilities.make_saxs_plot:run',
			'make_spec_models = mesmer.utilities.make_spec_models:run',
			'make_synthetic_target = mesmer.utilities.make_synthetic_target:run'
		]
	},
	
	zip_safe			= False,
)
