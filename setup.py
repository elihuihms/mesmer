#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

# MESMER - Minimal Ensemble Solutions to Multiple Experimental Restraints
# Copyright (C) 2015 SteelSnowflake Software LLC
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
import setuptools

if sys.version_info < (2, 6, 0):
    sys.stderr.write("MESMER requires Python 2.6 or newer.\n")
    sys.exit(-1)

#
# Do actual packaging now
#

install_requires = [
	'argparse>=1.0',
	'matplotlib>=1.3',
	'numpy>=1.3',
	'scipy>=0.11',
]

extras_requires = [
	'Bio>=1.5',
]

classifiers = [
	'Topic :: Scientific/Engineering',
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: GNU General Public License v2 (GPLv2)'
]

#
# Extensions and filenames to ignore when finding package data files
#

ignore_name = ['.DS_Store']
ignore_exts = ['.py','.pyc']

packages,package_data = ['mesmer'],{'':['LICENSE.txt']}
for dirname, dirnames, filenames in os.walk(packages[0]):
	
	for subdirname in dirnames:
		if subdirname[0] == '.':
			continue
		packages.append(os.path.join(dirname,subdirname).replace(os.sep,'.'))
	
	dirname = dirname.replace(os.sep,'.')
	for filename in filenames:
		if filename in ignore_name:
			continue
	
		if any([filename.endswith(e) for e in ignore_exts]):
			continue
		
		if dirname not in package_data:
			package_data[dirname] = []
		package_data[dirname].append( filename )
		
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

if __name__ == "__main__":
	import mesmer

	setuptools.setup(
		name				= 'MESMER',
		version				= mesmer.__version__,
		license				= mesmer.__license__,
		author				= mesmer.__author__,
		author_email		= mesmer.__author_email__,
		description			= mesmer.__description__,
		long_description	= open('README.txt').read(),
		url					= mesmer.__url__,
		download_url		= mesmer.__download_url__,
		platforms			= 'any',
		install_requires	= install_requires,
		extras_requires		= extras_requires,
		classifiers			= classifiers,
		packages			= packages,
		package_data		= package_data,
		entry_points		= entry_points,
		zip_safe			= False
	)
