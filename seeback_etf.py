import functools
import datetime
from datetime import date
from os import listdir

path = 'etfs/{0}'

state = {}
serial = []
tax_rate = 0.0001
codes = []
opts = []


def calc_func(func, part, days):
	return functools.partial(func, days, part)


def roc(days, data):
	index = data['index']
	if index - days < 0:
		print('{0} first roc{1} day is: {2}'.format(data['name'], days, data['history'][days]['date']))
		exit(0)
	if index >= len(data['history']):
		print('{0} index {1} is out of range'.format(data['name'], index))
		exit(0)
	price1 = data['history'][index]['price']
	price2 = data['history'][index - days]['price']
	return price1 / price2 - 1


def roc_date(name, part, date, days):
	for data in pack:
		if data['name'] == name:
			for i in range(0, len(data[part]['history'])):
				if data[part]['history'][i]['date'] == date:
					data[part]['index'] = i
					return roc(days, part, data)
				if data[part]['history'][i]['date'] > date:
					if i == 0:
						print(
							'{0} {1} first trade day: {2}'.format(data['name'], part, data[part]['history'][i]['date']))
					else:
						print('{0} {1} has no trade day: {2}'.format(data['name'], part, date))
					return


def bias(days, part, data):
	index = data[part]['index']
	if index - days < 0:
		print('{0} {1} first roc{2} day is: {3}'.format(data['name'], part, days, data[part]['history'][days]['date']))
		exit(0)
	if index >= len(data[part]['history']):
		print('{0} {1} index {2} is out of range'.format(data['name'], part, index))
		exit(0)
	total = 0
	for i in range(0, days):
		total += data[part]['history'][index - i]['price']
	return data[part]['history'][index]['price'] / (total / days) - 1


def bias_date(name, part, date, days):
	for data in codes:
		if data['name'] == name:
			for i in range(0, len(data[part]['history'])):
				if data[part]['history'][i]['date'] == date:
					data[part]['index'] = i
					return bias(days, part, data)
				if data[part]['history'][i]['date'] > date:
					if i == 0:
						print(
							'{0} {1} first trade day: {2}'.format(data['name'], part, data[part]['history'][i]['date']))
					else:
						print('{0} {1} has no trade day: {2}'.format(data['name'], part, date))
					return


def parse_all():
	for etf in listdir('etfs'):
		codes.append(parse(etf))


def parse(code):
	history = []
	data = {}
	for line in open(path.format(code)):
		if line == '':
			continue
		arr = line.split(',')
		day = {'date': arr[0], 'price': float(arr[2])}
		history.append(day)
	data['history'] = history
	data['begin'] = history[0]['begin']
	data['name'] = code
	data['index'] = 0
	return data


def set_index(code, begin):
	if begin < code['begin']:
		return
	for i in range(0, len(code['history'])):
		if code['history'][i]['date'] >= begin:
			code['index'] = i
			return


def pick(datas, d, func):
	n = -1
	for data in datas:
		if d.isoformat() < data['begin']:
			print('{} is not start in {}'.format(data['name'], d))
			continue
		if date_of(data) < d.isoformat():
			print('should not happen')
			exit(0)
		elif date_of(data) > d.isoformat():
			continue
		v = func(data, d)
		if n < v:
			n = v
			picked = data
	return picked


def date_of(code):
	return code['history'][code['index']]['date']


def price_of(code, offset=0):
	return code['history'][code['index'] + offset]['price']


def wealth():
	if state['stock']['num'] == 0:
		return state['balance']
	else:
		return price_of(state['stock']['data']['etf']) * state['stock']['num'] + state['balance']


def can_buy(m, price):
	return int(m / price / (1 + tax_rate) / 100) * 100


def pure_sell():
	state['balance'] += (price_of(state['stock']['data']['etf']) * state['stock']['num'] * (1 - tax_rate))
	data = state['stock']['data']
	print("{0} wealth: {6}, sell {1}, {2} * {3} = {4}, tax: {5}".format(
		data['point']['history'][data['point']['index']]['date'],
		data['etf']['code'], price_of(data['etf']), state['stock']['num'],
		price_of(state['stock']['data']['etf']) * state['stock']['num'],
		price_of(state['stock']['data']['etf']) * state['stock']['num'] * tax_rate, state['balance']))


def sell_end():
	state['stock'] = {'data': {}, 'price': 0, 'date': '', 'num': 0}
	state['buy'] = 0


def pure_buy(code):
	state['buy'] = state['balance']
	state['stock']['date'] = code['point']['history'][code['point']['index']]['date']
	state['stock']['data'] = code
	state['stock']['num'] = can_buy(state['balance'], price_of(code['etf']))
	state['balance'] -= state['stock']['num'] * price_of(code['etf']) * (1 + tax_rate)
	# print("{0} wealth: {7}, buy {1}, {2} * {3} = {4}, tax: {5}, balance: {6}".format(
	# 	data['point']['history'][data['point']['index']]['date'],
	# 	data['etf']['code'], price_of(data['etf']), state['stock']['num'],
	# 	price_of(data['etf']) * state['stock']['num'],
	# 	price_of(data['etf']) * state['stock']['num'] * tax_rate, state['balance'],
	# 	price_of(data['etf']) * state['stock']['num'] + state['balance']
	# ))
	record(code['point']['history'][code['point']['index']]['date'],
		   price_of(code['etf']) * state['stock']['num'] + state['balance'],
		   0, 'buy', code['etf']['code'], price_of(code['etf']), state['stock']['num'])


def record(date, w, ratio, o, code, price, num, tax_ratio=1):
	opts.append([date, w, ratio, o, code, price, num, price * num * tax_rate * tax_ratio])


def buy(code):
	pure_sell()
	pure_buy(code)


def sell():
	pure_sell()
	sell_end()


def summary():
	if not serial:
		print('current: {0}'.format(state['balance']))
		print(0)
	else:
		current = serial[-1]['wealth']
		# print('current: {0}'.format(current))
		print(current / state['init'] - 1, "")


def should_buy(func, days, part, data):
	if func(days, part, data) > 0 and state['stock']['data'] != data:
		return True
	return False


def should_sell(func, days, part, data):
	if func(days, part, data) < 0 and state['stock']['data'] != {}:
		return True
	return False


def should_buy_roc20_origin(data):
	return should_buy(roc, 20, data)


def should_sell_roc20_origin(data):
	return should_sell(roc, 20, data)


def should_buy_roc20_incr(data):
	if roc(20, 'point', data) > 0 and state['stock']['data'] != data and price_of(data['point']) > price_of(
			data['point'], -1):
		return True
	return False


def should_sell_roc20_decr(data):
	if roc(20, 'point', data) < 0 and state['stock']['data'] != {} and price_of(data['point']) < price_of(data['point'],
																										  -1):
		return True
	return False


def should_buy_bias20(data):
	if bias(20, 'point', data) > 0 and state['stock']['data'] != data:
		return True
	return False


def should_sell_bias20(data):
	if bias(20, 'point', data) < 0 and state['stock']['data'] != {}:
		return True
	return False


def init(money):
	state['balance'] = money
	state['init'] = money
	state['buy'] = 0
	state['stock'] = {'code': {}, 'price': 0, 'date': '', 'num': 0}


def end_of(data):
	return data['point']['history'][-1]['date']


def seeback(begin, pick_func, should_buy_func, should_sell_func, end='', money=1000000):
	init(money)
	for code in codes:
		set_index(code, begin)
	pack = codes
	begin_date = datetime.datetime.fromisoformat(begin).date()
	end_date = date.today() if end == '' else datetime.datetime.fromisoformat(end).date()
	while begin_date <= end_date:
		data = pick(pack, pick_func)
		date_index = data['history'][data['index']]['date']
		if end != '' and date > end:
			summary()
			break
		if should_buy_func(data):
			buy(data)
		elif should_sell_func(data):
			sell()
		serial.append({'date': date, 'wealth': wealth()})
		if date == end or date == end_of(data):
			summary()
			break
		for d in datas:
			d['point']['index'] += 1
			d['etf']['index'] += 1


def simple2(pick_days, opt_days):
	seeback(['sz50', 'cy50'], '2018-01-01', calc_func(roc, 'point', pick_days),
			lambda x: should_buy(roc, opt_days, 'point', x),
			lambda x: should_sell(roc, opt_days, 'point', x))


def diff_date(begin, end):
	f = True
	start = 0
	final = 0
	for w in serial:
		if f and w['date'] >= begin:
			start = w['wealth']
			f = False
		if w['date'] > end:
			break
		final = w['wealth']
	print('start: {0}, final: {1}'.format(start, final))
	print(final / start - 1)


if __name__ == '__main__':
	# parse_all()
	print('{}'.format(date.today()))
# simple2(20, 20)
