#!/usr/bin/env python

# MESMER - Minimal Ensemble Solutions to Multiple Experimental Restraints
# Copyright (C) 2018 SteelSnowflake Software LLC
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

import mesmer_cli
import mesmer_gui

from lib.util.get_ensemble_stats import GetEnsembleStats
#from lib.util.make_attribute_plot import MakeAttributePlot
#from lib.util.make_attribute_spec import MakeAttributeSpec
#from lib.util.make_components import MakeComponents
#from lib.util.make_correlation_plot import MakeCorrelationPlot
#from lib.util.make_curv_plot import MakeCURVPlot
#from lib.util.make_list_plot import MakeLISTPlot
#from lib.util.make_models import MakeModels
#from lib.util.make_saxs_plot import MakeSAXSPlot
#from lib.util.make_spec_models import MakeSpecModels
#from lib.util.make_synthetic_target import MakeSyntheticTarget

def cli():
	mesmer_cli.run()

def gui():
	mesmer_gui.run()

def get_ensemble_stats():
	GetEnsembleStats().exe()

def make_attribute_plot():
	MakeAttributePlot().exe()

def make_attribute_spec():
	MakeAttributeSpec().exe()

def make_components():
	MakeComponents().exe()

def make_correlation_plot():
	MakeCorrelationPlot().exe()

def make_curv_plot():
	MakeCURVPlot().exe()

def make_list_plot():
	MakeLISTPlot().exe()

def make_models():
	MakeModels().exe()

def make_saxs_plot():
	MakeSAXSPlot().exe()

def make_spec_models():
	MakeSpecModels().exe()

def make_synthetic_target():
	MakeSyntheticTarget().exe()

if __name__ == '__main__':
	cli()