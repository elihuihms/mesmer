types = {}

types['CURV'] = {
	'bool_options'	:[
		('Scaling','-scale',1,'Allow scaling of the ensemble curve to better fit the experimental data'),
		('Offset','-offset',1,'Allow the addition of a systematic offset to the ensemble curve to better fit the experimental data')
		],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[],
	'menu_options':{
		'Fitness'=>(
			{'Chisq'=>'','SSE'=>'-sse', 'Relative'=>'-relative','Poisson'=>'-poisson'},
			'Chisq',
			'Specifies how the fit to the experimental data is calculated.')
		}
	}

types['DEER'] = {
	'bool_options'	:[],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[],
	'menu_options'	:{}
	}

types['LIST'] = {
	'bool_options'	:[],
	'int_options'	:[('Data Column:','-col',1,'The column containing the data in the attached file')],
	'float_options'	:[],
	'string_options':[],
	'menu_options'	:{
		'Fitness'=>(
			{'SSE'=>'-sse','Relative'=>'relative','Quality Factor'=>'Q'},
			'',
			'Specifies how the fit to the experimental data is calculated.')
		}
	}

types['SAXS'] = {
	'bool_options'	:[
		('Scaling','-scale',1,'Allow scaling of the ensemble curve to better fit the experimental data'),
		('Offset','-offset',1,'Allow the addition of a systematic offset to the ensemble curve to better fit the experimental data')
		],
	'int_options'	:[],
	'float_options'	:[],
	'string_options':[],
	'menu_options'	:{}
	}
