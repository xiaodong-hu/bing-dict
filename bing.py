import requests
import re
from bs4 import BeautifulSoup
import os, sys
import json
from pathlib import Path

# Use Bing dictionary to inquery
def parse(keyword):
	#url1 = 'https://cn.bing.com/dict/search?q='
	#input() # phrases and sentences supported
	#url2 = 'FORM=Z9LH3' # set client position as USA
	#url = url1 + keyword
	#'http://dict.youdao.com/w/eng/hello/#keyfrom=dict2.index'
	proxyDict = {
		'http': 'http://192.168.3.69',
		'https': 'https://192.168.3.69',
	}

	url = 'https://cn.bing.com/dict/search?q=' + keyword
	try:
		r = requests.get(url, timeout=100)
	except:
		print('Link Failed !')
		exit()

	return BeautifulSoup(r.text, 'html.parser') # transfer to html files easy to analyse
'''
	sess = requests.Session()
	headers = {
		'Host': 'cn.bing.com',
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:50.0) Gecko/20180101 Firefox/50.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Language': 'en-US,zh-CN;q=0.5',
		'Accept-Encoding': 'gzip, deflate',
	}
	sess.headers.update(headers)
	url = 'https://cn.bing.com/dict/SerpHoverTrans?q=' + word
	try:
		r = sess.get(url, timeout=100, proxies = proxyDict)
	except:
		return None
'''

def words(soup):
	words_output = ''
	if soup.find('div', 'qdef'): # Necessary to avoid traceback 'Nontype', which is not iterable
		for s in soup.find('div', 'qdef'):
			translation = re.findall('<li>(.*?)</li>', str(s))
			for r in translation:
				characteristic = re.findall('<span class="pos">(.*?)</span>', str(r)) # this is a list of strings
				definition = re.findall('<span class="def">(.*?)</span>', str(r)) # this is a list of strings
				definition = re.sub('<.*?>','',definition[0]) # delete all futile links and tags in <a...>...</a>
				''' Differences of <.*> and <.*?>:
				Given 
					s = "<html><head><title>Title</title>"

				<.*>:最大(贪心)匹配
					print(re.match("<.*>", s).group())
				gives
					<html><head><title>Title</title>

				<.*?>:最小(非贪心)匹配
					print(re.match("<.*?>", s).group()
				gives
					<html>
				'''
				if len(characteristic)==1:
					# translation from website has the tag of class="web pos", so its characteristic should be empty
					words_output = words_output + '\n\t\033[94m\033[01m[' + characteristic[0] + ']\033[00m\t\033[93m' + definition + '\033[00m'
					# print('\t\033[94m\033[01m[{0}]\033[00m\t\033[93m{1}\033[00m'.format(characteristic[0],definition))
					# for colorful and boldface output in terminal, cf. stackexchange for more details, like https://stackoverflow.com/questions/287871/print-in-terminal-with-colors, or https://stackoverflow.com/questions/8924173/how-do-i-print-bold-text-in-python
				else:
					words_output = words_output + '\n\t\033[94m\033[01m[Web]\033[00m\t\033[93m' + definition + '\033[00m'
					#print('\t\033[94m\033[01m[Web]\033[00m\t\033[93m{}\033[00m'.format(definition))
	return words_output


def sentences(soup):
	num = 1
	sentences_output = ''
	for s in soup.find_all('div', 'se_li1'):
		if num<=5:
			# output only five sample sentences
			s = re.sub('<div class="sen_li">(.*?)</div>','',str(s)) # delete sources of example sentences
			#en_sentence = re.findall('<div class="sen_en">(.*?)<div>', s)
			#print(type(s))
			s = re.sub('<.*?>','',str(s))
			l = list(s)
			zh_sentence = re.sub(r'[A-Za-z0-9\%\-\(\)\;\:\?\!\,\.\'\"]','',str(s)) # delete all english parts of translation, then we're left with merely Chinese 
			zh_sentence = re.sub(' ','',str(zh_sentence))
			l_zh = list(zh_sentence)
			l_en = [i for i in l if i not in l_zh] # select all english parts of translation
			en_sentence = ''.join(l_en)

			sentences_output = sentences_output + '\n\n    \033[95m\033[01m' + str(num) + '. ' + '\033[00m' + en_sentence + '\n    ' + zh_sentence
			#print('\n    \033[95m\033[01m{0}.\033[00m {1}\n    {2}'.format(num, en_sentence, zh_sentence))
			num = num + 1

	return sentences_output


def query(soup, keyword):
	words_output = words(soup)
	sentences_output = sentences(soup)
	return words_output + sentences_output


if __name__ == '__main__':
	
	keyword = ' '.join(sys.argv[1:]) # argv[0] is the directory of current files, so we start form argv[1] and join the parameter list to string with spaces
	keyword_repeat = '\n    \033[32m\033[01m' + keyword + '\033[00m'

	soup = parse(keyword)
	'''
	soup = re.sub('<.*?>','',str(soup))
	soup = re.sub(r'<\![\[(.*?)\]\]>','',str(soup))
	print(str(soup))
	#str_keyword = ''
	'''
	data = {}
	translation = ''
	cache_filename = 'bing_cache.json'

	home = str(Path.home())
	# get the home directory, cf https://stackoverflow.com/questions/4028904/how-to-get-the-home-directory-in-python

	os.chdir(home) # always work in home directory

	try:
		with open(cache_filename, 'r', encoding='utf-8') as f: # open local cache file if exits, open with both read and write mode 
			data = json.load(f) # type is transformed from json to dict
			if str(keyword) in data: # check if keyword is in label
				print(data[str(keyword)])
			else:			
				data[str(keyword)] = keyword_repeat + query(soup, keyword) # input('Meaning: ')
				print(data[str(keyword)])
				with open(cache_filename, 'w', encoding='utf-8') as f: # add new cache at the end of local files
					json.dump(data, f, indent=4) #f.write(json.dumps(a, indent=4))	
	
	except IOError:
		
		if input('Cache File Not Exists. Creat a New One? (y/n) ') == 'y':

			f = open(cache_filename, 'w', encoding='utf-8') # creat new cache file if not exists
			f.write('{}')
			f.close()

			print('Cache File Created.')
		else:
			exit()

'''
	print('\n    \033[32m\033[01m{0}\033[00m\n'.format(keyword))
	
	if soup.find('div', 'qdef') is None:
		print('    \033[91m\033[01m No Found!\033[00m')
	else:
		words(soup)
		sentences(soup)
'''


'''
		print(re.findall('<li>(.*?)</li>',str(s),re.S)) # find the short translation
	#for s in soup.find('div','sentenceSeg')
	#	print(re.findall('<div class="se_li">'))
except:
	print('Cannot Find the Results!')
'''