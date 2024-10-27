THIS PROJECT IS DEPRECATED

Please don't use this project - There's nothing wrong with it per se, but MESMER was something I wrote to learn Python and Python GUIs while satisfying a scientific need I had in graduate school. As such, it contains a lot of dumb choices that you'd expect (and plenty of ones you might not expect) a novice python programmer to make. When I started writing MESMER, for example, Pandas was barely existent, and numpy/scipy documentation was still spotty, so there's lots of painfully slow manipulation of base Python datatypes instead of the fast vector math I should have used.

I did learn some valuable lessons that I'd like future programmers to be aware of, especially with regards to using HPC systems:
1. Leverage the ability of the argparse module to initiate runs from a text file.
2. Your GUI should work in tandem with a CLI, which allows you to configure your run on a desktop, and then copy the relevant files (including your run config text file) to a HPC system for execution.

Both of these lessons are demonstrated really well in Schrodinger's structural bioengineering suite of software. There was also a bit of a boom for a while in building GUI tools for Rosetta until AlphaFold ate their lunch. As an aside, Python GUI toolkits still suck even a dozen years later, and don't get me started on Electron.

I'll keep this project available but archived, as it was an important step in my journey as a scientific developer and definitely assisted me in making sense of the really confusing data I was getting from my experiments on TRAP + Anti-TRAP. Due to its shortcomings, it never really caught on as a replacement to Svergun's EOM (Sorry NMRBox). In fact, it could probably be replaced by a couple of jupyter notebooks that leverage the absolute powerhouse Pandas has become anyway. Minimal ensemble analysis approaches are such a niche need that a software package whose only claim to fame was possessing a GUI wasn't going to have a wide userbase anyway.

In closing, I'd like to encourage all scientists, especially those in grad school, to not blackbox the software they use. Reinventing the wheel a bit (when it comes to analyzing empirical data) can bring you closer to understanding nuances that are lost when you simply use a COTS package or adapt a coworker's existing code.

Be good to one another, and do good science.

Elihu Ihms, October 27th, 2024


Introduction
------------
MESMER (Minimal Ensemble Solutions to Multiple Experimental Restraints) is set of tools that enable structural biologists to identify and analyze characteristic structures or components from bulk-average data obtained from heterogenous solutions.

This is achieved by iteratively evolving a population of ensembles containing candidate components chosen from a large pool of potential structures, and selecting only ensembles that fit the available experimental data better than their peers.

MESMER is written exclusively in Python, and utilizes plugins in order to permit flexibility for analysis of nearly any datatype. A powerful GUI capable of generating protein conformations via Monte-Carlo randomization of backbone Phi/Psi angles, predicting the necessary component data, actually running MESMER, and subsequent analysis of results is also provided.

MESMER is licensed under the GPL v2 license, for details see LICENSE.txt

Installing and Running
----------------------
Released versions of MESMER are available from MESMER’s Github project page.

Uncompress the downloaded tarball or zip file, change into the directory, and type the following to install in the standard Python location:
    $ python setup.py install
    or
    $ sudo python setup.py install

Alternatively, you can place the MESMER directory in a location of your choosing, and add the mesmer and mesmer/utilities folder to your shell’s $PATH variable.

The latest development version can be retrieved from MESMER’s Github repository:
    $ git clone https://github.com/steelsnowflake/mesmer.git

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
    Biopython            http://biopython.org

Additional Help
---------------
Primary literature, a manual, and step-by step tutorials are available at http://steelsnowflake.com/downloads/?t=mesmer
