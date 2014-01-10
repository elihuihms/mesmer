__all__ = [
	'lib',
	'mesmer-gui',
	'mesmer',
	'plugins',
	'test',
	'utilities'
]

__license__			= u'GPL v2'
__author__			= u'Elihu Ihms'
__author_email__	= u'elihuihms@elihuihms.com'
__url__				= u'https://code.google.com/p/mesmer/'
__download_url__	= u'https://code.google.com/p/mesmer/downloads/list'

__description__		= u'MESMER: Identification of minimal ensembles from multiple structural biology datasets'
__long_description__ = u"""
MESMER (Minimal Ensemble Solutions to Multiple Experimental Restraints) is set of tools that enable structural biologists to identify and analyze characteristic structures or components from bulk-average data obtained from heterogenous solutions.

This is achieved by iteratively evolving a population of ensembles containing candidate components chosen from a large pool of potential structures, and selecting only ensembles that fit the available experimental data better than their peers.

MESMER is written exclusively in Python, and utilizes plugins in order to permit flexibility for analysis of nearly any datatype. A powerful GUI capable of predicting the necessary component data, running MESMER, and analyzing results is also provided.
"""

