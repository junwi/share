from Box import Box
from json import JSONEncoder


class Encoder(JSONEncoder):
	def default(self, o):
		return o.__dict__


class Run:
	path = '/Users/wangwei/stock/{0}.csv'

	@staticmethod
	def roc20(n, index, history):
		price1 = history[index]['price']
		price2 = history[index - n]['price']
		return price1 / price2 - 1

	def read(self, code):
		history = []
		for line in open(self.path.format(code)):
			if line == '':
				continue
			arr = line.split(',')
			day = {'date': arr[0], 'price': float(arr[2])}
			history.append(day)
		return history

	def __init__(self, configs, end, days, money=1000000):
		self.balance = money
		self.days = days
		self.end = end
		self.boxes = []
		for conf in configs:
			point = self.read(conf['point'])
			tail = 0
			if point[0]['date'] > end:
				print("{} begins after {}".format(conf.point, end))
				exit(0)
			for i in range(0, len(point)):
				if point[i]['date'] > end:
					break
				tail = i
			head = tail - days + 1
			cmp = []
			trade = []
			for i in range(head, tail + 1):
				cmp.append({'date': point[i]['date'], 'price': self.roc20(20, i, point)})
			begin = point[head]['date']
			etf = self.read(conf['etf'])
			for d in etf:
				if begin <= d['date'] <= end:
					trade.append(d)
			self.boxes.append(Box(etf, cmp, trade))

	def pick(self, pack):
		n = -1
		picked = None
		for code in pack:
			if code.higher(n):
				n =
			v = code.cmp[]
			if n < v:
				n = v
				picked = code
		return picked

	def run(self):
		while True:
			b = pick(self.boxes)

if __name__ == '__main__':
	confs = [
		{'name': 'sz50', 'point': 'sh000016', 'etf': 'sh510050'},
		{'name': 'cy50', 'point': 'sz399673', 'etf': 'sz159949'},
		{'name': 'zz1000', 'point': 'sh000852', 'etf': 'sh512100'}
	]
	r = Run(confs, '2021-08-24', 2)
	print(Encoder().encode(r))
