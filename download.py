# A股票行情数据获取演示   https://github.com/mpquant/Ashare
from Ashare import *


def download1():
	codes = ['sh000016', 'sz399673', 'sh000852', 'sh510050', 'sz159949', 'sh512100', 'sz399932', 'sz159928']
	for code in codes:
		df = get_price_sina(code, frequency='1d', count=10000)
		df.pop('volume')
		df.pop('high')
		df.pop('low')
		df.to_csv(r'~/stock/{0}.csv'.format(code), header=False)


def download2():
	for l in open('etf'):
		code = l.strip()
		if l.startswith("1"):
			code = 'sz' + code
		elif l.startswith('5'):
			code = 'sh' + code
		print(code)
		df = get_price_day_tx(code, frequency='1d', begin_date='2015-01-01', count=10000)
		df.pop('volume')
		df.pop('high')
		df.pop('low')
		df.to_csv(r'etfs/{0}'.format(l), header=False)


if __name__ == '__main__':
	download2()
