import sys
import copy
import datetime
import operator

from mesmer.errors import *
from mesmer.misc import mean_stdv
from mesmer.setup import set_module_paths
from mesmer.plugin import load_plugins

from mesmer.lib.input import *
from mesmer.lib.target import *
from mesmer.lib.component import *
from mesmer.lib.ensemble import *
from mesmer.lib.worker import *
from mesmer.lib.statistics import *
from mesmer.lib.output import *

class Optimizer(object):

	def __init__(self, logger, cli_args):
		"""
		Evolves a set of ensembles until a combination of components is found that best fits the provided target dataset

		Returns nothing, as all output is handled by other functions or plugin methods

		Args:
			logger (Logger): The logger to write to.
			cli_args (ArgumentParser): The command line parameters passed to MESMER.
		"""

		self.args = cli_args
		self.logger = logger

		# attempt to load available plugin modules
		self.plugins = []
		for id,ok,msg,module in load_plugins(set_module_paths(), 'mesmer', args=[self.args]):
			if ok:
				self.plugins.append( module )
			else:
				self.logger.warn( msg )

		if len(self.plugins) == 0:
			raise mesPluginError("No valid MESMER interpreter plugins found.")

		self.targets = load_targets( self.logger, self.args, self.plugins )
		self.components = load_components( self.logger, self.args, self.plugins, self.targets )
		self.in_queue = multiprocessing.Queue(maxsize=self.args.threads)
		self.out_queue = multiprocessing.Queue()

		self.workers = [None]*self.args.threads
		for i in xrange(self.args.threads):
			self.workers[i] = Worker(self)
			self.workers[i].start()

	def close(self):
		for w in self.workers:
			self.in_queue.put(None)	
		for w in self.workers:
			w.join()

		# finished, unload plugins
		try:
			unload_plugins( plugins )
		except mesPluginError as e:
			self.logger.exception(e)

		return

	def _optimize(self, ensembles, print_status=True):
		n,i = len(ensembles),0
		divisor = int(max(n/10,1))
		ret = []
		
		# submit ensembles to the queue
		for i in xrange(n):
			self.in_queue.put( ensembles[i] )
		
			if print_status and i % (divisor) == 0:
				self.logger.debug("Component ratio optimization progress: %i%%" % (100*i/n))
			
			# do we have any optimized ensembles to retrieve?
			try:
				ret.append( self.out_queue.get(False) )
			except:
				pass
		if print_status:
			self.logger.info("Component ratio optimization progress: 100%")

		# retrieve optimized ensembles
		while len(ret) < n:
			ret.append( self.out_queue.get(True) )
						
		return ret

	def _make_ensembles(self):
		"""
		Creates a set of ensembles using randomly selected components

		Returns a list of Ensembles"""

		component_names = self.components.keys()

		ret = []
		for i in range( self.args.ensembles ):
			ret.append( Ensemble( self.plugins, self.targets, self.args.size ) )

			# randomly fill the new ensemble with components
			if(not self.args.uniform):
				ret[-1].fill( component_names )
			else:
				ret[-1].fill_uniform( i, component_names )

		return ret

	def _evolve_ensembles(self, ensembles):
		"""
		Applies genetic transformations to the provided ensembles.
		These consist of:
		1. Crossing, where the components (genes) of two ensembles are swapped
		2. Mutation, where a component of an ensemble is switched with another component

		Args:
			ensembles (list of Ensemble): The ensembles to be worked upon"""

		# go through each evolution type separately
		for e in ensembles:

			# gene exchange (sexual) w/ random ensemble
			if(random.random() < self.args.Gcross):
				e.cross( random.choice(ensembles) )

		component_names = self.components.keys()

		for e in ensembles:
			# random mutation, either to any component, or a component present in the existing ensemble population
			e.mutate( component_names, ensembles, self.args.Gmutate, self.args.Gsource )

		return

	def _calculate_fitnesses(self, ensembles):
		"""
		Sum the fitness scores of every ensemble for each target

		Returns a target-name-keyed dict of scores for each ensemble

		Arguments:
		targets		- A list of mesTarget targets used to score the ensembles
		ensembles	- A list of mesEnsemble ensemble objects to be scored
		"""
		scores = {}
		for t in self.targets:
			scores[t.name] = []
			for e in ensembles:
				scores[t.name].append(sum(e.fitness[t.name].itervalues()))

		return scores

	def _get_best_ensembles( self, parents, offspring ):
		"""
		Return only the best-scoring ensembles from parent and offspring populations

		Arguments:
		parents (list of Ensembles): 
		offspring (list of Ensembles): 

		Returns a tuple of best scoring ensembles and some collected statistics
		(best_scored,stats)
		"""

		# calculate total fitness values for each population, parent and offspring
		p_scores = self._calculate_fitnesses( parents )
		o_scores = self._calculate_fitnesses( offspring )

		# combine the overall parent and offspring score sums into a list of key-score pairs
		scores = []

		for i in range( self.args.ensembles ):
			scores.append( [i, 0.0, 0.0] ) # third value will contain fuzzy value ensemble tolerance
			for t in self.targets:
				scores[-1][1] += p_scores[t.name][i]
			scores[-1][2] = scores[-1][1]

		for i in range( self.args.ensembles ):
			scores.append( [i +self.args.ensembles, 0.0, 0.0] )
			for t in self.targets:
				scores[-1][1] += o_scores[t.name][i]
			scores[-1][2] = scores[-1][1]
		
		score_min = min(zip(*scores)[1])
		if self.args.Gtolerance > 0: # add a small amount of variation to generate "fuzzy" tolerance during sorting
			for i in range( self.args.ensembles*2 ):
				scores[i][2] += scores[i][1] + (score_min * self.args.Gtolerance * random.random())

		# sort the array by the fitness scores
		sorted_scores = sorted(scores, key=operator.itemgetter(2))

		# keep track of per-target scores as well
		target_scores = {}
		for t in self.targets:
			target_scores[t.name] = []

		# select only the 1/2 best scoring from the combined parent and offspring ensembles for the next step
		best_scored, total_scores, fuzzy_scores = [], [], []
		counter = 0
		for (i, (key,score,fuzzy) ) in enumerate(sorted_scores):
			total_scores.append( score )
			fuzzy_scores.append( fuzzy )

			if( key < self.args.ensembles ):
				best_scored.append( parents[key] )
				for t in self.targets:
					target_scores[t.name].append( p_scores[t.name][key] )
			else:
				counter += 1
				best_scored.append( offspring[key % self.args.ensembles] )
				for t in self.targets:
					target_scores[t.name].append( o_scores[t.name][key % self.args.ensembles] )

			# quit once we've reached the required number of offspring
			if( i == (self.args.ensembles -1) ):
				break

		# calculate the minimum, average and stdev scores for the total and also for each target individually
		total_stats = [total_scores[0]]
		total_stats.extend(mean_stdv(total_scores))

		target_stats = {}
		for t in self.targets:
			target_stats[t.name] = [target_scores[t.name][0]]
			target_stats[t.name].extend(mean_stdv(target_scores[t.name]))

		# create the statistics dict
		stats = {
		'scores':	sorted_scores,
		'total':	total_stats,
		'target':	target_stats,
		'ratio':	float(self.args.ensembles - counter) / self.args.ensembles,
		'unique':	len(self._get_unique_ensembles(best_scored))
		}

		return (best_scored,stats)

	def _get_unique_ensembles(self, ensembles):

		# initialize the list with the first ensemble
		unique = [ ensembles[0] ]

		# only append ensembles that contain different components
		for e in ensembles:
			for seen in unique:
				if( set(seen.component_names) == set(e.component_names) ):
					break
			else:
				unique.append(e)

		return unique

	def _get_ratio_errors(self, ensembles):
		"""
		Determine the component ratio statistics for ensembles against each target

		Returns a list of ensemble componet ratio statistic dicts:
		[ensemble]
			|-{target}
				|-(component, weight, stdev)"""

		ret = []
		for e in ensembles:

			ratios = {}
			for t in self.targets:
				ratios[t.name] = []

			if(self.args.boots < 1):
				# no component ratio uncertainty analysis, just return the current ratios for each ensemble
				for t in self.targets:
					ratios[t.name].append( e.ratios[t.name] )
			else:
				# perform component ratio uncertainty analysis via bootstrap estimates

				divisor = max(int(self.args.boots/100),1)
				for i in range(self.args.boots):

					# make estimation of target restraints via bootstrapping
					estimates = []
					for t in self.targets:
						estimates.append( t.make_bootstrap(self.plugins,e) )

						# unset optimization flag!
						e.optimized[t.name] = False

					# optimize the component ratios
					optimized = self._optimize( [e], print_status=False )

					for t in self.targets:
						ratios[t.name].append( optimized[0].ratios[t.name] )

			# calculate the component ratio mean and standard deviation for each target
			temp = {}
			for t in self.targets:

				unzipped = zip(*ratios[t.name])

				temp[t.name] = []
				for i in range(self.args.size):
					mean,stdev = mean_stdv(unzipped[i])
					temp[t.name].append( [e.component_names[i],mean,stdev] )

				ret.append( temp )

		return ret

	def run(self):
		self.logger.info("Algorithm starting on %s." % datetime.datetime.utcnow() )
		
		self.logger.info("Creating parent ensembles..." )
		parents = self._make_ensembles()

		self.logger.info("Optimizing parent component ratios...")
		parents = self._optimize( parents )

		generation_counter = 0
		while( True ):
			self.logger.info( "Generation %i" % (generation_counter) )

			# create clones of the parents, and subject to genetic modification
			offspring = copy.deepcopy(parents)

			self.logger.info("Evolving offspring...")
			self._evolve_ensembles(offspring)

			# optimize component ratios for newly-mutated/crossed offspring
			self.logger.info("Optimizing offspring component ratios...")
			offspring = self._optimize(offspring)

			# retrieve the 1/2 best-scoring ensembles and some collected statistics
			(best_scored,ensemble_stats) = self._get_best_ensembles( parents, offspring )

			# get the relative fitness contribution for each restraint type
			restraint_stats = get_restraint_stats( self.args, self.targets, best_scored )

			# print the status and selected statistics
			log_generation_state( self.logger, self.args, generation_counter, ensemble_stats, restraint_stats )

			if(self.args.Pstats):
				# save component correlations from the current ensembles
				write_component_stats( self.logger, self.args, generation_counter, best_scored )

				# print collected information on the current ensembles
				write_ensemble_stats( self.logger, self.args, generation_counter, self.targets, best_scored )

			if(self.args.Pstate):
				# save the current ensemble population ratios
				write_ensemble_state( self.logger, self.args, generation_counter, self.targets, best_scored )

			if(self.args.Popt):
				# save the ratio optimization state for the current ensembles
				write_optimization_state( self.logger, self.args, generation_counter, self.targets, best_scored )

			if(self.args.Pbest):
				# print information about the best-scoring ensemble

				if(self.args.boots > 0):
					self.logger.info("Calculating best fit statistics...")

				# get the error intervals for the best ensemble component ratios
				best_ratio_errors = self._get_ratio_errors( [best_scored[0]] )
				log_ensemble_state( self.logger, self.args, best_ratio_errors[0] )

			if(self.args.Pextra):
				# call the various output methods of the plugins
				log_plugin_state( self.logger, self.args, generation_counter, self.plugins, self.targets, best_scored )

			# loop exit criteron
			if( ensemble_stats['scores'][self.args.size] < self.args.Fmin ):
				self.logger.info("Maximum ensemble score is less than Fmin, exiting.")
				return

			if( (ensemble_stats['total'][2]/ensemble_stats['total'][1]) < self.args.Smin ):
				self.logger.info("Ensemble score RSD is less than Smin, exiting.")
				return

			if (self.args.Gmax > -1) and (generation_counter >= self.args.Gmax):
				self.logger.info("Generation counter has reached Gmax, exiting.")
				return

			# set up for the next generation
			parents = best_scored
			generation_counter += 1

		self.close()

		return