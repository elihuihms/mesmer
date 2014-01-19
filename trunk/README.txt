Introduction
------------
MESMER (Minimal Ensemble Solutions to Multiple Experimental Restraints) is set of tools that enable structural biologists to identify and analyze characteristic structures or components from bulk-average data obtained from heterogenous solutions.

This is achieved by iteratively evolving a population of ensembles containing candidate components chosen from a large pool of potential structures, and selecting only ensembles that fit the available experimental data better than their peers.

MESMER is written exclusively in Python, and utilizes plugins in order to permit flexibility for analysis of nearly any datatype. A powerful GUI capable of predicting the necessary component data, running MESMER, and analyzing results is also provided.

MESMER is licensed under the GPL v2 license, for details see LICENSE.txt

Installing and Running
----------------------
Released versions of MESMER are available from MESMER’s Google Code project page.

Uncompress the downloaded tarball or zip file, change into the directory, and type the following to install in the standard Python location:
    $ python setup.py install
    or
    $ sudo python setup.py install

Alternatively, you can place the MESMER directory in a location of your choosing, and add the mesmer and mesmer/utilities folder to your shell’s $PATH variable.

The latest development version can be retrieved from MESMER’s Google Code SVN repository:
    $ svn checkout http://mesmer.googlecode.com/svn/mesmer

You should now be able to launch either the command-line version of mesmer, or the GUI:
    $ mesmer
    $ mesmer-gui

Prerequisites
-------------
MESMER requires at least Python 2.6

The following libraries are also required by MESMER:
    Tkinter/tK           http://www.tcl.tk/
    numpy,scipy          http://numpy.scipy.org
    matplotlib           http://matplotlib.sourceforge.net

The following libraries may also be required for some MESMER plugins to function correctly:
    Biopython            http://biopython.org

Additional Help
---------------
Primary literature, a manual, and step-by step tutorials are available at http://code.google.com/p/mesmer
