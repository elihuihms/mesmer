class mesError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class mesSetupError(mesError):
	pass
	
class mesPluginError(mesError):
	pass
	
class mesTargetError(mesError):
	pass

class mesComponentError(mesError):
	pass

class ComponentGenException(mesError):
	pass
	
class ModelExtractionException(mesError):
	pass