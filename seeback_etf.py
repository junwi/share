import functools
import datetime
from datetime import date, timedelta
from os import listdir

path = 'etfs/{0}'

state = {}
serial = []
tax_rate = 0.0001
codes = []
opts = []


def calc_func(func, days):
	return functools.partial(func, days)


def roc(days, code):
	index = code['index']
	if index - days < 0:
		return -1
	if index >= len(code['history']):
		print('{} index {} is out of range'.format(code['code'], index))
		exit(0)
	price1 = code['history'][index]['price']
	price2 = code['history'][index - days]['price']
	return price1 / price2 - 1


def roc_date(name, d, days, pack):
	for data in pack:
		if data['name'] == name:
			for i in range(0, len(data['history'])):
				if data['history'][i]['date'] == d:
					data['index'] = i
					return roc(days, data)
				if data['history'][i]['date'] > d:
					if i == 0:
						print(
							'{} first trade day: {}'.format(data['name'], data['history'][i]['date']))
					else:
						print('{} has no trade day: {}'.format(data['name'], d))
					return


def bias(days, data):
	index = data['index']
	if index - days < 0:
		print('{} first roc{} day is: {}'.format(data['name'], days, data['history'][days]['date']))
		exit(0)
	if index >= len(data['history']):
		print('{} index {} is out of range'.format(data['name'], index))
		exit(0)
	total = 0
	for i in range(0, days):
		total += data['history'][index - i]['price']
	return data['history'][index]['price'] / (total / days) - 1


def bias_date(name, d, days, pack):
	for data in pack:
		if data['name'] == name:
			for i in range(0, len(data['history'])):
				if data['history'][i]['date'] == d:
					data['index'] = i
					return bias(days, data)
				if data['history'][i]['date'] > d:
					if i == 0:
						print(
							'{} first trade day: {}'.format(data['name'], data['history'][i]['date']))
					else:
						print('{} has no trade day: {}'.format(data['name'], d))
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
	data['begin'] = history[0]['date']
	data['code'] = code.strip()
	data['index'] = 0
	return data


def set_index(code, begin):
	if begin < code['begin']:
		return
	for i in range(0, len(code['history'])):
		if code['history'][i]['date'] >= begin:
			code['index'] = i
			return


def pick(pack, d, func):
	n = -1
	picked = None
	if not can_sell(d):
		return
	for code in pack:
		if d < code['begin']:
			# print('{} is not start in {}'.format(data['code'], d))
			continue
		if date_of(code) < d:
			print('should not happen')
			exit(0)
		elif date_of(code) > d:
			continue
		v = func(code)
		if n < v:
			n = v
			picked = code
	return picked


def date_of(code):
	if code['index'] >= len(code['history']):
		return '9999-99-99'
	return code['history'][code['index']]['date']


def price_of(code, offset=0):
	return code['history'][code['index'] + offset]['price']


def wealth():
	if state['stock']['num'] == 0:
		return state['balance']
	else:
		return price_of(state['stock']['code']) * state['stock']['num'] + state['balance']


def can_sell(d):
	if state['stock']['code'] == {}:
		return True
	if date_of(state['stock']['code']) < d:
		print('should not happen in can_sell')
		exit(0)
	if date_of(state['stock']['code']) > d:
		print('{} can not sell in {}'.format(state['stock']['code']['code'], d))
	return date_of(state['stock']['code']) == d


def can_buy(m, price):
	return int(m / price / (1 + tax_rate) / 100) * 100


def pure_sell():
	state['balance'] += (price_of(state['stock']['code']) * state['stock']['num'] * (1 - tax_rate))
	code = state['stock']['code']
	print("{} wealth: {}, sell {}, {} * {} = {}, tax: {}".format(
		date_of(code),
		state['balance'],
		code['code'], price_of(code), state['stock']['num'],
		price_of(state['stock']['code']) * state['stock']['num'],
		price_of(state['stock']['code']) * state['stock']['num'] * tax_rate))


def sell_end():
	state['stock'] = {'code': {}, 'price': 0, 'date': '', 'num': 0}
	state['buy'] = 0


def pure_buy(code):
	state['buy'] = state['balance']
	state['stock']['date'] = date_of(code)
	state['stock']['code'] = code
	state['stock']['num'] = can_buy(state['balance'], price_of(code))
	state['balance'] -= state['stock']['num'] * price_of(code) * (1 + tax_rate)
	print("{0} wealth: {7}, buy {1}, {2} * {3} = {4}, tax: {5}, balance: {6}".format(
		code['history'][code['index']]['date'],
		code['code'], price_of(code), state['stock']['num'],
		price_of(code) * state['stock']['num'],
		price_of(code) * state['stock']['num'] * tax_rate, state['balance'],
		price_of(code) * state['stock']['num'] + state['balance']
	))
	record(code['history'][code['index']]['date'],
		   price_of(code) * state['stock']['num'] + state['balance'],
		   0, 'buy', code['code'], price_of(code), state['stock']['num'])


def record(date, w, ratio, o, code, price, num, tax_ratio=1):
	opts.append([date, w, ratio, o, code, price, num, price * num * tax_rate * tax_ratio])


def buy(code):
	if state['stock']['code']:
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


def should_buy(func, days, code):
	if func(days, code) > 0 and state['stock']['code'] != code:
		return True
	return False


def should_sell(func, days, code):
	if func(days, code) < 0 and state['stock']['code'] != {}:
		return True
	return False


def should_buy_roc20_origin(data):
	return should_buy(roc, 20, data)


def should_sell_roc20_origin(data):
	return should_sell(roc, 20, data)


def should_buy_roc20_incr(data):
	if roc(20, data) > 0 and state['stock']['code'] != data and price_of(data) > price_of(
			data, -1):
		return True
	return False


def should_sell_roc20_decr(data):
	if roc(20, data) < 0 and state['stock']['code'] != {} and price_of(data) < price_of(data, -1):
		return True
	return False


def should_buy_bias20(data):
	if bias(20, data) > 0 and state['stock']['code'] != data:
		return True
	return False


def should_sell_bias20(data):
	if bias(20, data) < 0 and state['stock']['code'] != {}:
		return True
	return False


def init(money):
	state['balance'] = money
	state['init'] = money
	state['buy'] = 0
	state['stock'] = {'code': {}, 'price': 0, 'date': '', 'num': 0}


def end_of(code):
	return code['history'][-1]['date']


def seeback(begin, pick_func, should_buy_func, should_sell_func, end='', money=1000000):
	init(money)
	for code in codes:
		set_index(code, begin)
	pack = codes
	begin_date = datetime.datetime.fromisoformat(begin).date()
	end_date = date.today() if end == '' else datetime.datetime.fromisoformat(end).date()
	while begin_date <= end_date:
		d = begin_date.isoformat()
		data = pick(pack, d, pick_func)
		if data:
			if should_buy_func(data):
				buy(data)
			elif should_sell_func(data):
				sell()
			serial.append({'date': date, 'wealth': wealth()})
			if date == end or date == end_of(data):
				summary()
				break
		else:
			print('skip', d)
		forward(pack, d)
		begin_date = begin_date + timedelta(1)
	summary()


def forward(pack, d):
	for code in pack:
		if date_of(code) == d:
			code['index'] += 1


def simple2(pick_days, opt_days):
	seeback('2021-01-01', calc_func(roc, pick_days),
			lambda x: should_buy(roc, opt_days, x),
			lambda x: should_sell(roc, opt_days, x))


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
	parse_all()
	simple2(1, 5)
