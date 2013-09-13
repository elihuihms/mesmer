class mesSetupError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class mesPluginError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class mesTargetError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class mesComponentError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg