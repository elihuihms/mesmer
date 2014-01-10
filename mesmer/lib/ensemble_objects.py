import random

from exceptions			import *
from utility_functions	import print_msg,get_input_blocks

class mesEnsemble:
	"""
	A collection of components, their relative ratios, and once calculated, their fitness when compared to a target
	"""

	def __init__(self, plugins, targets, size):
		"""
		Initialize the object's properties to sane starting values

		Arguments:
		plugins - The plugin modules
		targets	- The targets this ensemble will be evaluated against
		size	- The size (number of components) in the ensembles
		"""

		self.size = size
		self.component_names = [''] * self.size

		self.optimized = {}
		self.opt_status = {}
		self.ratios = {}
		self.fitness = {}
		self.plugin_data = {}

		for t in targets:
			self.optimized[t.name] = False
			self.opt_status[t.name] = None
			self.ratios[t.name] = [1.0/self.size] * self.size
			self.fitness[t.name] = {}

			self.plugin_data[t.name] = {}
			for p in plugins:
				for type in p.type:
					self.plugin_data[t.name][type] = {}
					self.fitness[t.name][type] = 0.0

		return

	def fill(self, component_names):

		self.component_names = []
		while(len(self.component_names) < self.size):
			c = random.choice(component_names)

			# enforce non-duplicate components
			if( c not in self.component_names ):
				self.component_names.append( c )

		return

	def fill_uniform(self, index, component_names):

		n = len(component_names)
		self.component_names = [None]*self.size
		for i in range(self.size):
			if( component_names[index] not in self.component_names ):
				self.component_names[i] = component_names[index]
			elif( index+i >= n ):
				self.component_names[i] = component_names[i]
			else:
				self.component_names[i] = component_names[index+i]

		return

	def set_optimized( self, value=False ):
		for t in self.optimized:
			self.optimized[t] = value
		return

	def mutate( self, component_names, ensembles, Gmutate, Gsource ):
		"""
		Mutates the current ensemble by randomly exchanging conformers with either the total population or those present in other existing ensembles

		Returns nothing.

		Arguments:
		components	- A list of all components to be used in the case of extra-ensemble mutation
		ensembles	- A list of all ensembles to be used in the case of intra-ensemble mutation
		Gmutate		- A float determining the probability each component in the ensemble will be mutated
		Gsource		- A float determining the source of the mutated component
		"""

		for i in range( self.size ):

			# mutate this component?
			if( random.random() < (Gmutate / self.size) ):

				if( random.random() < Gsource ): # mutate to a randomly-selected component from the pool
					name = random.choice( component_names )
					if (name not in self.component_names):
						self.component_names[ i ] = name

				else: # mutate to a randomly-selected component from one present in another ensemble
					e = random.choice( ensembles )
					name = random.choice( e.component_names )
					if (name not in self.component_names):
						self.component_names[ i ] = name

				self.set_optimized(False)

		return

	def cross( self, partner, Ex=0.5 ):
		"""
		Crosses the current ensemble with another, resulting in a mutual exchange of components.

		Returns nothing.

		Arguments:
		partner	- The partner ensemble with which to exchange components
		Ex		- The fraction of components to exchange (defaults to 0.5, meaning that on average 1/2 of components will be exchanged)

		"""

		# perform 50% probabilistic exchanges between the partners
		for i in range( self.size ):
			if( random.random() < Ex):

				# check and make sure we won't be creating duplicates in the resulting ensembles
				if (self.component_names[i] not in partner.component_names) and (partner.component_names[i] not in self.component_names):

					# neat trick to swap components
					(self.component_names[i],partner.component_names[i]) = (partner.component_names[i],self.component_names[i])

					# unset partner and self optimization flags
					self.set_optimized(False)
					partner.set_optimized(False)

		return

	def normalize(self, target_name):
		"""
		Normalizes the ensemble's component ratios for a given target, returns nothing.

		Arguments:
		target	- mesTarget, the target for whose weights we are normalizing
		"""

		total = sum(self.ratios[target_name])
		if( total == 0 ):
			self.ratios[target_name] = [1.0/self.size] * self.size
		else:
			for i in range(self.size):
				self.ratios[target_name][i] = self.ratios[target_name][i] / total

		return

	def get_fitness(self, components, plugins, target, ratios):
		"""
		Calculate the fitness of the ensemble for a given target and component ratios
		Saves the calculated fitness back to the object as well

		Returns the sum of all restraint/attribute discrepancies

		Arguments:
		components	- The component database
		plugins		- The plugin modules used to calculate the target-solution discrepancy
		target		- The restraint-containing mesTarget to evaluate fitness against
		ratios		- The weighting vector used to determine each component's contribute to the solution
		"""

		# always keep our component ratios normalized
		self.ratios[target.name] = ratios
		self.normalize(target.name)

		# set our optimization status to dirty (calling function will have to set this back)
		self.optimized[target.name] = False

		for r in target.restraints:

			# build a list of our attributes to average together for a fit to the target data
			attributes = []

			# find the plugin to handle this type of data
			for name in self.component_names:
				for a in components[name].attributes:
					if( a.restraint.type == r.type ):
						attributes.append( a )

			# hand off the collected attributes to the correct plugin to score
			for p in plugins:
				if( r.type in p.type ):
					self.fitness[target.name][r.type] = r.scale * p.calc_fitness( r, target.plugin_data[r.type], self.plugin_data[target.name][r.type], attributes, self.ratios[target.name] )
					
		return self.fitness[target.name]
