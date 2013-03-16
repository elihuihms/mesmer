### MESMER Tutorial / Quickstart Guide ###
March 15th, 2013 - Elihu Ihms

### INTRODUCTION ###
MESMER is a powerful tool that can identify the elements present in heterogeneous experimental samples from bulk-average data. This is done by generating fits to the experimental data (the "target") built up from predicted data calculated from one or more elements - the "components". Components are candidate models that may or may not be actually present in the actual experimental conditions, but which (hopefully) sample the range of structural or other variability present in the system.

### INSTALLATION ###
MESMER is entirely written in Python, and other than requiring the Python 2.6 interpreter and several common libraries, requires no compilation. The required libraries are:
1. Scipy (scipy.org)
2. Matplotlib (matplotlib.org) - required for on-the-fly fit plot generation

Note: Enthought (www.enthought.com) makes easy-to-use installers containing both Python and the aforementioned libraries for Windows, Mac OSX, and linux operating systems.

To install MESMER, untar the compressed tarball in the desired directory at the command line prompt:
prompt> tar -xvf mesmer_<version>.tgz

MESMER is now ready to use. For convenience, the MESMER executable and various utilities can be added to the user's PATH via the .cshrc or .bash_profile files present in the user's home directory.

For bash shells, append this to your .bash_profile (replace the /path/to/mesmer with the actual location of MESMER):
export PATH=$PATH:/path/to/mesmer/mesmer

For csh or tcsh shells, append this to your .cshrc:
set PATH = ($PATH /path/to/mesmer/mesmer)

### GENERATION OF COMPONENT FILES ###
The first step of MESMER fitting is to generate files containing the pre-calculated attributes (stoichiometries, SAXS profiles, FRET distances, etc.) of all possible components. The MESMER utility make_components collects these attributes and generates properly-formatted input files.

For the purposes of this tutorial, the component stoichiometries, SAXS profiles, and FRET lifetime curves for 18 different theoretical structures have already been computed. These data are present in the file "component_values.tbl" and the directories "saxs_data", and "fret_data" respectively. The "make_components" utility will combine these data into properly-formatted MESMER component files guided by the provided template: "component_template.txt".

To run make_components, type the following at the command line when inside the "tutorials" directory:
prompt> ../utilities/make_components -template ./component_template.txt -values ./component_values.tbl -data ./saxs_data -data ./fret_data -out components

This will create the directory "components", and fill it with component files. These files can be inspected in any text editor, as they are simply ASCII text.

The target files containing the synthetic experimental data are already formatted, and are similar in structure to component files. They are also consist of ASCII text and can be viewed and edited with any text editor. For the purposes of the tutorial, the targets are the combined data of two or more components with 1% added gaussian noise:

tutorial_A: 50% component 00000, 50% component 00014
tutorial_B: 40% component 00000, 40% component 00014, 20% component 00017

### IMPORTANT MESMER PARAMETERS ###
Central to MESMER's function is the ensemble. This is a collection of 1 or more components that together will be used to create a fit to experimental data. The relative contribution of each component can be automatically varied by MESMER to provide the best fit through a number of optimization methods. The number of components per ensemble is set via the "-size <#>" option.

Instead of utilizing just one ensemble, MESMER simultaneously evolves a large population of ensembles, each initially containing a randomized collection of components. MESMER will evaluate the fitness of each ensemble (a better fit to the experimental data = more fitness), and ensembles that possess a greater fitness (i.e. fit the experimental data better) will go on to the next generation, while ensembles that fit the experimental data poorly will be discarded. To generate variability, at each generation clones of the best-performing previous generation will be subjected to random mutation (component replacement) or crossing (component exchange).

### TESTING CONFORMERS ###
To test the formatting of the conformer files and the availability of the required libraries, try and run a single MESMER generation from within the tutorial folder:
prompt> ../mesmer -size 1 -ensembles 10 -Gmax 0 -target ./tutorial_A_saxs.target -components ./components

In order, MESMER will:
1. Print the parameters for the run,
2. Load the input component files,
3. Create the initial parent ensembles,
4. Optimize the parent ensemble's relative component weights,
5. Perform one round of mutation and crossing to create offspring ensembles,
6. Exit.

At each generation, the relative contribution of each restraint type will be displayed (best, average, and distribution). After each generation, only the 1/2 best scoring ensembles of both the parent and offspring ensemble populations combined will be retained. The "parent survival percentage" is the ratio of parent ensembles that have survived competition with their mutated and crossed offspring, and will typically increase once ensembles that fit the experimental data well have been evolved.

NOTE: By default, MESMER will save all a log of its progress and other output files in the directory specified using the "-name <dirname>" option. If no name is specified, the results will be saved in a directory "MESMER_Results". MESMER will not overwrite the directory from a previous run unless the -force (force overwrite) command is provided.

NOTE: To see a list of all available MESMER options along with a brief description of each, invoke MESMER with only the "-h" (help) option.

### FITTING SAXS DATA ###
For a meaningful MESMER run, typically the iterative process of offspring generation and optimization should be continued until all ensembles fit the experimental data equally well or nearly so. This can be done by specifying by the "-Smin <#>" (Standard deviation minimum) option. This will cause the genetic algorithm to exit only when the standard deviation of the ensemble's scoring function is at or below the specified value.

To run MESMER until all ensembles have a total fitness score (in this example the chi-square fit to the target SAXS profile) standard deviation of 0.1 or less, invoke MESMER as follows:
prompt> ../mesmer -size 3 -Smin 0.1 -target ./tutorial_A_saxs.target -components ./components -name tutorial_1

You may wish to go get a coffee, depending on the processing power of the machine MESMER is running on. If you have a computer with multiple cores or processors, you will likely see a significant decrease in computation time by using the "-threads <#>" command to specify the number of parallel processing threads you wish to use. You can also change the ensemble population size by using the "-ensembles <#>" command (the default is 1000 ensembles, which is likely excessive when using only 18 different components.)

### INTERPRETING MESMER OUTPUT ###
If you open the last "ensemble_statistics_NNNNN.tbl" file present in the output folder "tutorial_1" created by the above MESMER run, you should see some statistics about the components present in the ensemble population at MESMER's final generation. The "Prevalence" value is the percentage that the component appears in the total ensemble population (100% = is present in all ensembles, 0% = present in no ensembles). This is important because it is often the case that multiple components can provide equal or similar fitness to their respective ensembles (they may be indistinguishable from each other, for example). The "Average" value is the average weight of that component in its ensembles (a larger average indicates that it is more heavily weighted in the ensemble averaged data used to fit the experimental data). Finally, the "Stdev" column is the variation in the component weighting across the ensemble population.

The synthetic target "tutorial_A_saxs.target" used in the above run is the equally-weighted predicted SAXS profiles data of two components (00000 and 00014) averaged together to which 1% gaussian noise has been added. Because of this, the components 00000 and 00014 should be highly prevalent in the ensemble population. Note also that the average weighting for these components is roughly 1/2. Component 00015, which possesses a SAXS curve very similar to 00014, will also be present. Because three components (via the "-size <#>" option) were used per ensemble to fit the synthetic data but only two components are needed to obtain a good fit, the remaining components are lightly-weighted and should show little consensus in their prevalence in the ensemble population. In the following example, FRET lifetime data in conjunction with SAXS data will be used to distinguish between the similar components 00014 and 00015.

### FITTING MULTIPLE DATATYPES ###
MESMER can simultaneously fit any number of experimental datasets, provided the user has generated the necessary predicted data for each component. The "tutorial_A_all.target" contains the average component stoichiometry, a SAXS profile, and a CURV (non-specific 2D dataset) containing fluoresence lifetime data from components 00000 and 00014, with added 1% noise. MESMER will automatically detect these different data types, and will load the appropriate plugin to generate ensemble fits from the available components. For example:
prompt> ../mesmer -size 3 -Smin 0.1 -target ./tutorial_A_all.target -components ./components -name tutorial_2

An examination of the last ensemble statistics file generated by MESMER should reveal that only the components 00000 and 00014 are conclusively identified in the ensemble population.

### FITTING MULTIPLE TARGETS ###
MESMER is also capable of simultaneously fitting ensembles to multiple targets. This is especially useful when analyzing titration data, where the experimenter expects to find the same components but in different amounts. MESMER will optimize the relative contributions of the components for each ensemble against each target separately. To do multi-target fitting, one need only provide multiple "-target <target_file>" options. 

### OBTAINING ENSEMBLE STATISTICS AND FITS ###
By default, MESMER only saves two pieces of information at each generation:
1. The score of the best-fitting ensemble and average score of the ensemble population. (Saved to the mesmer_log.txt file in the output directory)
2. The components present in the entire population and information about their weighting in their respective ensembles. (See the "ensemble_statistics_NNNNN.tbl" files in MESMER's output directory).

MESMER can also calculate the uncertainty in component ratios of a given ensemble through bootstrap error analysis. Because this can be computationally expensive, it is only performed on the best-fitting ensemble. It can be enabled with the "-Pbest" (Print best statistics) option, along with the number of bootstrap error replicates to perform "-boots <#>". The default is 200 replicates.

Depending on the restraint type, MESMER can also save the experimental data and MESMER's fit results for the best-scoring ensemble through the use of the "-Pextra" (Print extra) option. This will notify MESMER plugins to print and/or save any extra information that may be useful for the user to the log file or results directory. Files generated by plugins will follow this format: restraints_(target name)_(restraint type)_NNNNN.out

To generate these various output files, and apply all the elements covered in the tutorial, run MESMER with these options:
prompt> ../mesmer -size 3 -Smin 0.1 -target ./tutorial_A_all.target -target ./tutorial_B_all.target -components ./components -Pstats -Pbest -Pextra -name tutorial_3


