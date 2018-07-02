class mesError(Exception):
	def __init__(self, msg, errno=1):
		self.msg = msg
		self.errno = errno
	def __str__(self):
		return "%s (%i)"%(self.msg,self.errno)

class mesSetupError(mesError):
	pass
	
class mesPluginError(mesError):
	pass
	
class mesUtilityError(mesError):
	pass
	
class mesTargetError(mesError):
	pass

class mesComponentError(mesError):
	pass

class ComponentGenException(mesError):
	pass
	
class ModelExtractionException(mesError):
	pass