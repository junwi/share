import functools

path = 'data1/{0}'

pack = [
	{'name': 'sz50', 'point': {'code': 'sh000016'}, 'etf': {'code': 'sh510050'}},
	{'name': 'cy50', 'point': {'code': 'sz399673'}, 'etf': {'code': 'sz159949'}},
	{'name': 'zz1000', 'point': {'code': 'sh000852'}, 'etf': {'code': 'sh512100'}},
	{'name': 'zzxf', 'point': {'code': 'sz399932'}, 'etf': {'code': 'sz159928'}},
	{'name': 'hs300', 'point': {'code': 'sz399300'}, 'etf': {'code': 'sh510300'}},
	# {'name': 'zz500', 'point': {'code': 'sh000905'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'zzyh', 'point': {'code': 'sz399986'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'zzbj', 'point': {'code': 'sz399997'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'zzyy', 'point': {'code': 'sz399933'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'zzmt', 'point': {'code': 'sz399998'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'zzmt', 'point': {'code': 'sz399998'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'xny', 'point': {'code': 'sh000941'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'gzxp', 'point': {'code': 'sz980017'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'gzys', 'point': {'code': 'sz399395'}, 'etf': {'code': 'sh510500'}},
	# {'name': 'gzgt', 'point': {'code': 'sz399440'}, 'etf': {'code': 'sh510500'}},
]

state = {}
serial = []
tax_rate = 0.0001
opts = []


def calc_func(func, part, days):
	return functools.partial(func, days, part)


def roc(days, part, data):
	index = data[part]['index']
	if index - days < 0:
		print('{0} {1} first roc{2} day is: {3}'.format(data['name'], part, days, data[part]['history'][days]['date']))
		exit(0)
	if index >= len(data[part]['history']):
		print('{0} {1} index {2} is out of range'.format(data['name'], part, index))
		exit(0)
	price1 = data[part]['history'][index]['price']
	price2 = data[part]['history'][index - days]['price']
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
	for data in pack:
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
	for data in pack:
		parse(data, 'point')
		parse(data, 'etf')


def parse(data, part):
	history = []
	for line in open(path.format(data[part]['code'])):
		if line == '':
			continue
		arr = line.split(',')
		day = {'date': arr[0], 'price': float(arr[2])}
		history.append(day)
	data[part]['history'] = history
	data[part]['begin'] = history[0]['date']


def set_index(data, part, begin):
	if begin < data[part]['begin']:
		print('{0} {1} first buy day is: {2}'.format(data['name'], part, data[part]['begin']))
		exit(0)
	for i in range(0, len(data[part]['history'])):
		if data[part]['history'][i]['date'] >= begin:
			data[part]['index'] = i
			return


def verify():
	codes = []
	for data in pack:
		data['point']['index'] = -1
		data['etf']['index'] = -1
		codes.append(data['point'])
		codes.append(data['etf'])
	e = earliest(codes)
	e['index'] = 0
	started = [e]
	end = False
	while True:
		if end:
			return
		date = ''
		for code in started:
			code['index'] += 1
			if code['index'] == len(code['history']):
				# print('touch end of {0} with date {1}'.format(code['code'], code['history'][code['index'] - 1]['date']))
				end = True
			elif date == '':
				date = code['history'][code['index']]['date']
			elif code['history'][code['index']]['date'] != date:
				print('{0} has no date'.format(code['code'], date))
				exit(0)
		for code in started:
			if code['index'] != len(code['history']) and end:
				print('{0} is not end'.format(code['code']))
		for code in codes:
			if code['index'] == -1:
				if code['history'][0]['date'] == date:
					code['index'] = 0
					started.append(code)
				elif code['history'][0]['date'] < date:
					print('{0} has date {1} cause conflict'.format(code['code'], date))
					exit(0)


def earliest(codes):
	e = {}
	for code in codes:
		if e == {} or e['history'][0]['date'] > code['history'][0]['date']:
			e = code
	return e


def pick(datas, func):
	n = -1
	for data in datas:
		v = func(data)
		if n < v:
			n = v
			picked = data
	return picked


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
	data = state['stock']['data']
	if not data:
		return
	state['balance'] += (price_of(data['etf']) * state['stock']['num'] * (1 - tax_rate))
	record(data['point']['history'][data['point']['index']]['date'], state['balance'],
		   state['balance'] / state['buy'] - 1,
		   'sell', data['etf']['code'], price_of(data['etf']), state['stock']['num'])
	# print("{0} wealth: {6}, ratio: {7}, sell {1}, {2} * {3} = {4}, tax: {5}".format(
	# 	data['point']['history'][data['point']['index']]['date'],
	# 	data['etf']['code'], price_of(data['etf']), state['stock']['num'],
	# 	price_of(state['stock']['data']['etf']) * state['stock']['num'],
	# 	price_of(state['stock']['data']['etf']) * state['stock']['num'] * tax_rate, state['balance'],
	# 	state['balance'] / state['buy'] - 1)
	# )
	state['stock'] = {'data': {}, 'price': 0, 'date': '', 'num': 0}
	state['buy'] = 0


def record(date, w, ratio, o, code, price, num, tax_ratio=1):
	opts.append([date, w, ratio, o, code, price, num, price * num * tax_rate * tax_ratio])


def sell_end():
	pass


def pure_buy(data):
	state['buy'] = state['balance']
	state['stock']['date'] = data['point']['history'][data['point']['index']]['date']
	state['stock']['data'] = data
	state['stock']['num'] = can_buy(state['balance'], price_of(data['etf']))
	state['balance'] -= state['stock']['num'] * price_of(data['etf']) * (1 + tax_rate)
	# print("{0} wealth: {7}, buy {1}, {2} * {3} = {4}, tax: {5}, balance: {6}".format(
	# 	data['point']['history'][data['point']['index']]['date'],
	# 	data['etf']['code'], price_of(data['etf']), state['stock']['num'],
	# 	price_of(data['etf']) * state['stock']['num'],
	# 	price_of(data['etf']) * state['stock']['num'] * tax_rate, state['balance'],
	# 	price_of(data['etf']) * state['stock']['num'] + state['balance']
	# ))
	record(data['point']['history'][data['point']['index']]['date'],
		   price_of(data['etf']) * state['stock']['num'] + state['balance'],
		   0, 'buy', data['etf']['code'], price_of(data['etf']), state['stock']['num'])


def buy(data):
	pure_sell()
	pure_buy(data)


def sell():
	pure_sell()
	sell_end()


def summary():
	if state['stock']['data'] != {}:
		data = state['stock']['data']
		record(state['date'], wealth(), wealth() / state['buy'] - 1,
			   'hold', data['etf']['code'], price_of(data['etf']), state['stock']['num'], 0)
	else:
		record(state['date'], wealth(), 0, 'empty', '-', 0, 0)
	if len(opts) > 0:
		headers = ['date', 'wealth', 'ratio', 'operation', 'code', 'price', 'num', 'tax']
	# 	print('\t'.join(headers))
	# for o in opts:
	# 	print('\t'.join(str(x) for x in o))
	print(wealth())


# if not serial:
# 	print('current: {0}'.format(state['balance']))
# 	print(0)
# else:
# 	current = serial[-1]['wealth']
# 	# print('current: {0}'.format(current))
# 	print(current / state['init'] - 1, "")


def should_buy(func, days, part, data):
	if func(days, part, data) > 0 and state['stock']['data'] != data and bias(100, part, data) > 0:
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
	state['stock'] = {'data': {}, 'price': 0, 'date': '', 'num': 0}


def end_of(data):
	return data['point']['history'][-1]['date']


def seeback(choose, begin, pick_func, should_buy_func, should_sell_func, end='', money=1000000):
	init(money)
	datas = []
	for n in choose:
		for data in pack:
			if data['name'] == n:
				set_index(data, 'point', begin)
				set_index(data, 'etf', begin)
				datas.append(data)
	while True:
		data = pick_func(datas)# pick(datas, pick_func)
		date = data['point']['history'][data['point']['index']]['date']
		state['date'] = date
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


def pick_2_round(pack, round1_num, round1_func, round2_func):
	round1 = []
	for data in pack:
		round1.append([round1_func(data), data])
	round1.sort(key=lambda x: x[0], reverse=True)
	if len(round1) <= round1_num:
		round2 = round1
	else:
		round2 = round1[0:round1_num]
	return pick([x[1] for x in round2], round2_func)


def simple2round(round1, round2, opt):
	seeback(['cy50', 'hs300', 'zzxf', 'zz1000'], '2020-12-31',
				lambda x: pick_2_round(x, 2, calc_func(roc, 'point', round1), calc_func(roc, 'point', round2)),
			lambda x: should_buy(roc, opt, 'point', x),
			lambda x: should_sell(roc, opt, 'point', x), end='2021-12-31')


def simple2(pick_days, opt_days):
	seeback(['cy50', 'sz50'],                    '2020-12-31',
			lambda x: pick(x, calc_func(roc, 'point', pick_days)),
			lambda x: should_buy(roc, opt_days, 'point', x),
			lambda x: should_sell(roc, opt_days, 'point', x), end='2021-12-31')


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
	print('start: {0}, final: {1}'.format(begin, end))
	print(final / start - 1)


if __name__ == '__main__':
	parse_all()
	# verify()

	# simple2round(40, 20, 20)
	simple2(20, 20)
