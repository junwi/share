class Box:
	def __init__(self, name, cmp, trade):
		self.name = name
		self.cmp = cmp
		self.trade = trade
		self.index = 0

	def higher(self, v):
		return self.cmp[self.index] > v
