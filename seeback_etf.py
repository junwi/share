import functools
import datetime
from datetime import date, timedelta
from os import listdir

path = 'etfs/{0}'

etf_name = {}
state = {}
serial = []
tax_rate = 0.0001
codes = []
opts = []
lines = [5, 10, 20, 30, 60]

def calc_func(func, days):
	return functools.partial(func, days)


def roc(days, code):
	index = code['index']
	return roc_index(days, index, code)


def roc_index(days, index, code):
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
					return roc_index(days, i, data)
				if data['history'][i]['date'] > d:
					if i == 0:
						print(
							'{} first trade day: {}'.format(data['name'], data['history'][i]['date']))
					else:
						print('{} has no trade day: {}'.format(data['name'], d))
					return


def bias(days, code):
	index = code['index']
	return bias_index(days, index, code)


def bias_index(days, index, code):
	if index - days < -1:
		# print('{} first bias{} day is: {}'.format(code['code'], days, code['history'][0]['date']))
		return 0
	if index >= len(code['history']):
		print('{} index {} is out of range'.format(code['code'], index))
		return 0
	total = 0
	for i in range(0, days):
		total += code['history'][index - i]['price']
	return code['history'][index]['price'] / (total / days) - 1


def bias_date(name, d, days, pack):
	for data in pack:
		if data['code'] == name:
			for i in range(0, len(data['history'])):
				if data['history'][i]['date'] == d:
					return bias_index(days, i, data)
				if data['history'][i]['date'] > d:
					if i == 0:
						print(
							'{} first trade day: {}'.format(data['name'], data['history'][i]['date']))
					else:
						print('{} has no trade day: {}'.format(data['name'], d))
					return 0


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
	return date_of(state['stock']['code']) == d


def can_buy(m, price):
	return int(m / price / (1 + tax_rate) / 100) * 100


def pure_sell():
	state['balance'] += (price_of(state['stock']['code']) * state['stock']['num'] * (1 - tax_rate))
	code = state['stock']['code']
	print("{} rate: {}, wealth: {}, sell {}".format(
		date_of(code),
		state['balance'] / state['buy'] - 1,
		state['balance'],
		code['code']
	))


def sell_end():
	state['stock'] = {'code': {}, 'price': 0, 'date': '', 'num': 0}
	state['buy'] = 0


def pure_buy(code):
	state['buy'] = state['balance']
	state['stock']['date'] = date_of(code)
	state['stock']['code'] = code
	state['stock']['num'] = can_buy(state['balance'], price_of(code))
	state['balance'] -= state['stock']['num'] * price_of(code) * (1 + tax_rate)
	print('{} buy {}'.format(date_of(code), code['code']))
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


def forward(pack, d):
	for code in pack:
		if date_of(code) == d:
			code['index'] += 1


def choose_week(day, n, candidates, old):
	if day.weekday() != 0:
		return old
	l = []
	for etf in candidates:
		v = roc_of(15, etf, day.isoformat())
		if v > 0:
			l.append([v, etf])
	l.sort(key=lambda x: x[0], reverse=True)
	if len(l) < n:
		r = l
	else:
		r = l[0:n]
	print([(x[1]['code'], x[0]) for x in r])
	return [x[1] for x in r]


def roc_of(n, etf, d):
	index = -1
	if etf['begin'] > d:
		return 0
	for i in range(0, len(etf['history'])):
		if etf['history'][i]['date'] >= d:
			index = i - 1
			break
	if index - n < 0:
		return 0
	return etf['history'][index]['price'] / etf['history'][index - n]['price'] - 1


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


def seeback(begin, pick_func, should_buy_func, should_sell_func, end='', money=1000000):
	init(money)
	for code in codes:
		set_index(code, begin)
	pack = codes
	begin_date = datetime.datetime.fromisoformat(begin).date()
	end_date = date.today() if end == '' else datetime.datetime.fromisoformat(end).date()
	old = []
	while begin_date <= end_date:
		d = begin_date.isoformat()
		choose = choose_week(begin_date, 2, pack, old)
		old = choose
		data = pick(choose, d, pick_func)
		if data:
			if should_buy_func(data):
				buy(data)
			elif should_sell_func(data):
				sell()
			serial.append({'date': date, 'wealth': wealth()})
			if date == end or date == end_of(data):
				summary()
				break
		forward(pack, d)
		begin_date = begin_date + timedelta(1)
	summary()


def simple2(pick_days, long_days):
	seeback('2021-01-01', calc_func(roc, pick_days),
			lambda x: should_buy(roc, long_days, x),
			lambda x: should_sell(roc, long_days, x))


def calc_history(pack, func, days):
	for code in pack:
		if len(code['history']) < days:
			for h in code['history']:
				h['v'] = 0
			continue
		for i in range(0, days):
			code['history'][i]['v'] = 0
		for i in range(days, len(code['history'])):
			code['history'][i]['v'] = func(days, i, code)


def find_longest(pack, begin, end):
	d = 0
	r = {}
	for code in pack:
		l = {'d': 0, 'periods': []}
		n = {'d': 0, 'days': []}
		for h in code['history']:
			if begin <= h['date'] <= end:
				if h['v'] > 0:
					n['d'] += 1
					n['days'].append(h)
					if n['d'] == l['d']:
						l['periods'].append(n['days'])
					elif n['d'] > l['d']:
						l['d'] = n['d']
						l['periods'] = [n['days']]
				else:
					n = {'d': 0, 'days': []}
		if l['d'] > d:
			d = l['d']
			r = {code['code']: l['periods']}
		elif l['d'] == d:
			r[code['code']] = l['periods']
	print(begin, end)
	print('longest', d)
	for code, periods in r.items():
		print(code)
		for period in periods:
			s = period[0]
			e = period[-1]
			print('from {} to {}, incr {:.2f}%'.format(s['date'], e['date'], (e['price'] / s['price'] - 1) * 100))


def last_longest(pack, day_num):
	r = {}
	for code in pack:
		n = []
		for h in reversed(code['history']):
			n.append(h)
			if h['v'] <= 0:
				break
			if code['code'] not in r:
				r[code['code']] = n
	c = []
	for code, days in r.items():
		e = days[0]
		e1 = days[1]
		s = days[-1]
		if code not in etf_name:
			print(code)
			continue
		c.append([code, etf_name[code], 'from {} to {}, total {:.2f}%, last {:.2f}%'
				 .format(s['date'], e['date'], (e['price'] / s['price'] - 1) * 100, (e['price'] / e1['price'] - 1) * 100), len(days), e['date']])
	c.sort(key=lambda x: x[3], reverse=True)
	n = 0
	for s in c:
		flag = False
		for line in lines:
			if line <= day_num:
				continue
			if bias_date(s[0], s[4], line, codes) <= 0:
				flag = True
				break
		if flag:
			continue
		if s[3] != n:
			n = s[3]
			print(n - 1)
		print(s[0], s[1].strip(), s[2])


def parse_etf_name():
	for line in open('etf_name'):
		arr = line.split(',')
		if len(arr) < 2:
			continue
		etf_name[arr[0]] = arr[1]


if __name__ == '__main__':
	parse_all()
	parse_etf_name()
	calc_history(codes, roc_index, 1)
	last_longest(codes, 10)
