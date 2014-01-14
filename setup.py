#!/usr/bin/env python

# MESMER - Minimal Ensemble Solutions to Multiple Experimental Restraints
# Copyright (C) 2014 Elihu Ihms
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
	'mesmer.utilities',
	'mesmer.plugins',
]

package_data = {
	'':
		['LICENSE.txt'],
	'mesmer.lib.gui':
		['mesmer_logo.gif']
}

plugin_packages = [
	'mesmer.plugins.gui_c_deer_lib',
	'mesmer.plugins.gui_c_fret_lib',
	'mesmer.plugins.pyParaTools'
]

plugin_data = {
	'mesmer.plugins.pyParaTools':
		['CHANGES.txt','LICENSE.txt']
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

from setuptools import setup

import mesmer
import mesmer.lib

packages.extend( plugin_packages )
for d in plugin_data:
	package_data[d] = plugin_data[d]

setup(
	name	= 'MESMER',
	version	= mesmer.lib.__version__,
	license	= mesmer.__license__,
	author	= mesmer.__author__,
	author_email = mesmer.__author_email__,
	description	= mesmer.__description__,
	long_description	= open('README.txt').read(),
	url	= mesmer.__url__,
	download_url = mesmer.__download_url__,
	platforms	= 'any',
	requires	= requires,
	classifiers	= classifiers,
	packages	= packages,
	package_data	= package_data,
	entry_points	= entry_points,
	zip_safe	= False
)
