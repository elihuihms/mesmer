#!/usr/bin/env python

import os
import sys

if sys.version_info < (2, 5, 0):
    sys.stderr.write("MESMER requires Python 2.5 or newer.\n")
    sys.exit(-1)

# Warn the user that the GUI will be noop if Tk is not available:
try:
	import Tkinter
except ImportError:
	s = raw_input("WARNING: Tkinter is not installed, the GUI will not be available, continue? (Y/N): ")
	if s[0]!='Y' and s[0]!='y':
		exit()
		
# put default plugin-specific imports here
try:
	import Bio
except ImportError:
	s = raw_input("WARNING: Biopython is not installed, some plugins may not work properly, continue? (Y/N): ")
	if s[0]!='Y' and s[0]!='y':
		exit()
		
#
# Do actual packaging now
#

from setuptools import setup

requires = [
	'argparse',
	'numpy',
	'scipy',
	'matplotlib'
]

classifiers = [
	'Topic :: Scientific/Engineering',
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
]

packages = [
	'mesmer',
	'mesmer.lib',
	'mesmer.lib.gui',
	'mesmer.utilities'
]

package_data = {
	'mesmer.lib.gui':
		['mesmer_logo.gif'],
	'mesmer':
		['plugins/*.py']
}

entry_points = {
	'console_scripts': [
		'mesmer = mesmer.mesmer:run',
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
}

import mesmer
import mesmer.lib

setup(
	name	= 'MESMER',
	version	= mesmer.lib.__version__,
	license	= mesmer.__license__,
	author	= mesmer.__author__,
	author_email = mesmer.__author_email__,
	description	= mesmer.__description__,
	long_description	= mesmer.__long_description__,
	url	= mesmer.__url__,
	download_url = mesmer.__download_url__,
	platforms	= 'any',
	requires	= requires,
	classifiers	= classifiers,
	packages	= packages,
	package_data	= package_data,
	entry_points	= entry_points
)
