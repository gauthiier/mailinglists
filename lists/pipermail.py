import urllib.request, urllib.parse
import logging, os, sys, traceback, re, time, json, gzip, difflib
from bs4 import BeautifulSoup
import lists.mhonarc

DELAY = 0.2

def collect_from_url(url, name, base_archive_dir):

	response = urllib.request.urlopen(url)
	html = response.read().decode(encoding="utf-8")
	soup = BeautifulSoup(html, "html5lib")

	threads_list = soup.find_all('tr')
	lists = []
	for t in threads_list[1:]:
		cols = t.find_all('td')
		if len(cols) < 2:
			continue
		thread_label = cols[0].text.strip()[:-1]
		thread_url = cols[1].select('a:nth-of-type(1)')[0].get('href') 	# this is relative
		url = (url + "/") if not url.endswith('/') else url
		thread_url = urllib.parse.urljoin(url, thread_url)
		lists.append((thread_label, thread_url)) 						# list of tuples

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
	html = response.read().decode(encoding="utf-8")
	soup = BeautifulSoup(html, "html5lib")

	ul = soup.find_all('ul')[1];
	lists = ul.find_all('li', recursive=False)

	is_mhonarc_hybrid = soup.find(text=re.compile('MHonArc')) is not None

	#lists = soup.select('ul:nth-of-type(2)')[0].find_all('li', recursive=False)
	nbr_msgs = str(len(lists))
	n = 0		
	for li in lists:
		n += 1
		logging.info("	> " + str(n) + "/" + nbr_msgs)
		try:
			if is_mhonarc_hybrid:
				logging.info("Mhonarc detected, switching to mhonarc parsing...")
				thread = archive_thread_hybrid_mhonarc(li, url.replace('thread.html', ''), None)
			else:
				thread = archive_thread(li, url.replace('thread.html', ''), None)
			threads['threads'].append(thread)
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

	return threads

def archive_thread(li, base_url, parent_thread_data):

	thread_a = li.select('a:nth-of-type(1)')[0]
	url = (base_url + "/") if not base_url.endswith('/') else base_url
	thread_url = urllib.parse.urljoin(url, thread_a.get("href"))	
	thread_title = thread_a.text.strip()

	# this may not always be there... 
	# ex. http://lists.cofa.unsw.edu.au/pipermail/empyre/2007-September/thread.html
	thread_id = li.select('a:nth-of-type(2)')[0].get("name")
	thread_author_name = li.select('i')[0].text.strip()

	message = {u'id': thread_id, u'subject': thread_title, u'url': thread_url, u'author_name': thread_author_name}

	collect_message(thread_url, message)
	
	ul = li.find_all('ul');
	if len(ul) == 0:
		if parent_thread_data is None:
			return message

		if u'follow-up' not in parent_thread_data:
			parent_thread_data[u'follow-up'] = []
		parent_thread_data[u'follow-up'].append(message)
		return message


	follow = ul[0].find_all('li', recursive=False)	
	if len(follow) > 0:
		for f in follow:
			follow_a = f.select('a')
			if len(follow_a) > 0:
				archive_thread(f, base_url, message)
		
	if parent_thread_data is None:
		return message

	if u'follow-up' not in parent_thread_data:
		parent_thread_data[u'follow-up'] = []
	parent_thread_data[u'follow-up'].append(message)
	return message

def archive_thread_hybrid_mhonarc(li, base_url, parent_thread_data):

	thread_a = li.select('a:nth-of-type(1)')[0]
	url = (base_url + "/") if not base_url.endswith('/') else base_url
	thread_url = urllib.parse.urljoin(url, thread_a.get("href"))	
	thread_title = thread_a.text.strip()

	thread_id = thread_a.get("name")
	thread_author_name = 'n/a'

	message = {u'id': thread_id, u'subject': thread_title, u'url': thread_url, u'author_name': thread_author_name}

	lists.mhonarc.collect_message(thread_url, message)
	
	ul = li.find_all('ul');
	if len(ul) == 0:
		if parent_thread_data is None:
			return message

		if u'follow-up' not in parent_thread_data:
			parent_thread_data[u'follow-up'] = []
		parent_thread_data[u'follow-up'].append(message)
		return message


	follow = ul[0].find_all('li', recursive=False)	
	if len(follow) > 0:
		for f in follow:
			follow_a = f.select('a')
			if len(follow_a) > 0:
				archive_thread_hybrid_mhonarc(f, base_url, message)
		
	if parent_thread_data is None:
		return message

	if u'follow-up' not in parent_thread_data:
		parent_thread_data[u'follow-up'] = []
	parent_thread_data[u'follow-up'].append(message)
	return message	

def collect_message(url, message):
	# logging.info("	+ " + url)

	response = urllib.request.urlopen(url)
	html = response.read().decode(encoding="utf-8")
	soup = BeautifulSoup(html, "html5lib")

	if lists.mhonarc.test_xcomment(soup):
		logging.info("Mhonarc detected, switching to mhonarc parsing...")
		lists.mhonarc.collect_message(url, message)

	#message_labels = ('to', 'subject', 'from', 'date', 'message-id', 'content-type')

	message['subject'] = soup.select('h1:nth-of-type(1)')[0].text.strip()
	message['author_name'] = soup.select('b:nth-of-type(1)')[0].text.strip()
	message['from'] = soup.select('a:nth-of-type(1)')[0].text.strip()
	message['date'] = soup.select('i:nth-of-type(1)')[0].text.strip()
	message['message-id'] = message['id']
	message['content-type'] = 'n/a'

	message['content'] = soup.select('pre:nth-of-type(1)')[0].text


