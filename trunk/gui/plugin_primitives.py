class GUICalcPluginError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class GUICalcPlugin():

	def __init__(self):
		return True

