# A股票行情数据获取演示   https://github.com/mpquant/Ashare
from Ashare import *


def download1():
	codes = ['sh000016', 'sz399673', 'sh000852', 'sh510050', 'sz159949', 'sh512100', 'sz399932', 'sz159928', 'sz399300',
			 'sh510300', 'sh000905', 'sh510500', 'sh000933', 'sh512010']
	for code in codes:
		df = get_price_sina(code, frequency='1d', count=10000)
		df.pop('volume')
		df.pop('high')
		df.pop('low')
		df.to_csv(r'data1/{0}'.format(code), header=False)


def download2():
	with open('etf_name', 'w') as etf_name:
		for l in open('etf'):
			code = l.strip()
			if l.startswith("1"):
				code = 'sz' + code
			elif l.startswith('5'):
				code = 'sh' + code
			print(l)
			df, name = get_price_day_tx(code, frequency='1d', begin_date='2015-01-01', count=10000)
			etf_name.write('{},{}\n'.format(l.strip(), name))
			df.pop('volume')
			df.pop('high')
			df.pop('low')
			df.to_csv(r'etfs/{0}'.format(l), header=False)


import re


class LazyDecoder(json.JSONDecoder):
	def decode(self, s, **kwargs):
		regex_replacements = [
			(re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
			(re.compile(r',(\s*])'), r'\1'),
		]
		for regex, replacement in regex_replacements:
			s = regex.sub(replacement, s)
		return super().decode(s, **kwargs)


def download3():
	url = 'http://96.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112406074246312303457_1608308070107&pn=1&pz=5000&po=0&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f12,f14&_=1608308070112'
	s = str(requests.get(url).content, encoding='utf8')
	s = s[s.index('(') + 1:s.index(')')]
	data = json.loads(s, cls=LazyDecoder)
	with open('stock_name', 'w') as stock_name:
		for l in data['data']['diff']:
			stock_name.write('{},{}\n'.format(l['f12'], l['f14']))
			code = l['f12']
			if code.startswith('0') or code.startswith('3'):
				code = 'sz' + code
			else:
				code = 'sh' + code
			save_data(code, 'stocks/{0}'.format(l['f12']))
			print(l['f12'])


def save_data(code, path):
	data = get_price_day_json_tx(code, frequency='1d', count=10000)
	if len(data) == 0:
		return
	with open(path, 'w') as stock:
		for d in data:
			if len(d) > 6:
				d = d[0:6]
			stock.write(','.join(d) + '\n')


if __name__ == '__main__':
	download1()
