types = {}

types['CURV'] = {
	'bool_options'	:[
		('Scaling','scale',1,'Allow scaling of the ensemble curve to better fit the experimental data'),
		('Offset','offset',1,'Allow the addition of a systematic offset to the ensemble curve to better fit the experimental data'),
		('Fitness: SSE','sse',0,'Return fitness as a sum-squared of error'),
		('Fitness: Relative','relative',0,'Return fitness as determined by relative deviation'),
		('Fitness: Poisson','poisson',0,'Return fitness as determined by Poisson error distribution'),
		('Datatype: DEER','deer',0,'Fit DEER data by optimizing the modulation depth of ensemble DEER curve'),
		('Datatype: SAXS','saxs',0,'Treat the data as small-angle X-ray or neutron scattering data.')
		],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[]
	}

types['DEER'] = {
	'bool_options'	:[],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[]
	}

types['LIST'] = {
	'bool_options'	:[
		('Fitness: SSE','sse',0,'Return fitness as a sum-squared of error'),
		('Fitness: Relative','relative',0,'Return fitness as determined by relative deviation'),
		('Fitness: Quality Factor','Q',0,'Return fitness as a quality factor, propotional to the experimental data RMSD')
		],
	'int_options'	:[('Data Column:','col',1,'The column containing the data in the attached file')],
	'float_options'	:[],
	'string_options':[]
	}

types['SAXS'] = {
	'bool_options'	:[
		('Scaling','scale',1,'Allow scaling of the ensemble curve to better fit the experimental data'),
		('Offset','offset',1,'Allow the addition of a systematic offset to the ensemble curve to better fit the experimental data')
		],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[]
	}
