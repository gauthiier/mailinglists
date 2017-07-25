import urllib.request, urllib.parse
import logging, os, sys, traceback, re, time, json, gzip, difflib
from bs4 import BeautifulSoup


DELAY = 0.2

def collect_from_url(url, name, base_archive_dir):

	response = urllib.request.urlopen(url)
	#html = response.read().decode(encoding="utf-8")
	html = response.read()
	soup = BeautifulSoup(html, "html5lib")

	threads_list = soup.find_all('tr', {'class': 'normalgroup'})[0].find_all('li')
	lists = []
	for t in threads_list:
		thread_label = t.text.strip()
		thread_url = urllib.parse.urljoin(url, t.select('a')[0].get('href'))
		lists.append((thread_label, thread_url))

	# create (main) directory 
	# this is where all temp files will be created
	d = os.path.join(base_archive_dir, name)
	if not os.path.exists(d):
		os.makedirs(d)		

	threads = []
	nbr_threads = str(len(lists))
	n = 0
	for l in lists: ### change this
		n += 1
		logging.info("## " + str(n) + " / " + nbr_threads + " ##")
		try:
			threads.append(collect_threads_from_url(name=l[0], url=l[1], base_arch_dir=d))
		except KeyboardInterrupt:
			sys.exit(0)					
		except:
			logging.warning("Error archiving: " + l[1] + "... Continuing.")
			ex_t, ex, tb = sys.exc_info()
			print(ex_t)
			traceback.print_tb(tb)
			del tb
			continue

def collect_threads_from_url(url, name, base_arch_dir):

	threads = {'name' : name, 'url' : url, 'threads' : []}
	
	logging.info("Collecting threads of: " + name)

	arch_name = name.replace(' ', '_')

	# check if archive already exists
	file_path = os.path.join(base_arch_dir, arch_name + '.json')
	if os.path.isfile(file_path):
		logging.info("archive " + name + " already exists. loading from file " + file_path)
		with open(file_path, 'r') as fin:
			try:
				threads = json.load(fin)
				return threads  
			except:
				logging.info("can't open archive " + file_path + "... rearchiving.")


	response = urllib.request.urlopen(url)
	#html = response.read().decode(encoding="utf-8")
	html = response.read()
	soup = BeautifulSoup(html, "html5lib")

	table = soup.find_all('table', {'class': 'tableframe'})[1].find_all('tr')
	lists = []
	for tr in table:
		if tr.has_attr('class') and (tr['class'][0] == 'normalgroup' or tr['class'][0] == 'emphasizedgroup'):
			lists.append(tr)

	# the thread structure here is flat -- re: non-hierarchical, unlike pipermail
	# hence the thread parsing algorithm will also be flat -- re: a single loop

	nbr_msgs = str(len(lists))
	n = 0	
	last_message = None	
	for tr in lists:
		n += 1
		logging.info("	> " + str(n) + "/" + nbr_msgs)
		td = tr.find_all('td')
		thread_a = td[0].select("p span a")[0]
		thread_url = urllib.parse.urljoin(url, thread_a.get("href"))
		thread_title = thread_a.text.strip()

		try:

			message = {u'id': 0, u'subject': thread_title, u'url': thread_url, u'author_name': 'n/a'}

			threads['threads'].append(collect_message(thread_url, message))

			if last_message and similar(last_message['subject'], message['subject']):
				if u'follow-up' not in last_message:
					last_message[u'follow-up'] = []
				print(message['subject'] + " - follows - " + last_message['subject'])
				last_message[u'follow-up'].append(message)

			else:
				last_message = message

		except KeyboardInterrupt:
			sys.exit(0)		
		except:
			ex_t, ex, tb = sys.exc_info()
			print(ex_t)
			traceback.print_tb(tb)
			del tb
			continue

		time.sleep(DELAY)	

	logging.info("writing archive to file " + file_path)

	with open(file_path, 'w') as fp:
		json.dump(threads, fp, indent=4)

	logging.info("done.")


def collect_message(url, message):

	response = urllib.request.urlopen(url)
	#html = response.read().decode(encoding="utf-8")
	html = response.read()
	soup = BeautifulSoup(html, "html5lib")

	tr = soup.find_all('table', {'class': 'tableframe'})[3].find_all('tbody', recursive=False)[0].find_all('tr', recursive=False)

	header = tr[0].find_all('tbody')[0].find_all('tr', recursive=False)
	message['subject'] = header[0].select("p a")[0].text.strip()
	message['from'] = header[1].select("p")[1].text.replace("<[log in to unmask]>", "").strip()
	message['author_name'] = message['from']
	message['date'] = header[3].select("p")[1].text.strip()
	message['content-type'] = header[4].select("p")[1].text.strip()

	message['content'] = tr[1].find_all('pre')[0].text	

	return message


def similar(str_a, str_b):
	r = difflib.SequenceMatcher(None, str_a, str_b).ratio()
	return r > 0.75

