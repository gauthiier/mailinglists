import urllib.request, urllib.parse
import logging, os, sys, traceback, re, time, json, gzip
from bs4 import BeautifulSoup

DELAY = 0.2

def collect_from_url(url, sublist_name, base_arch_dir="archives", mbox=False):

    response = urllib.request.urlopen(url)
    html = response.read().decode(encoding="utf-8")
    soup = BeautifulSoup(html, "html5lib")

    # base url 
    base_url = soup.select('body p:nth-of-type(2) base')[0].get('href')

	#collect name
    list_name = soup.select('body p:nth-of-type(2) base title')[0].string
    logging.info("Getting " + list_name + " list archive for " + sublist_name)

    lists = soup.select('ul:nth-of-type(2) li')

    threads = []

    for l in lists:

    	if l.strong is None:
    		continue

    	name = l.strong.string

    	if name.lower() == sublist_name.lower():

            threads_url_list = []
            threads_links = l.select('ul li a')
            for t in threads_links:
                thread_url = urlparse.urljoin(base_url, t.get('href'))
                threads_url_list.append(thread_url)

            nbr_threads = str(len(threads_url_list))
            n = 0

            for u in threads_url_list:
                n += 1
                logging.info("## " + str(n) + " / " + nbr_threads + " ##")
                threads.append(collect_threads_from_url(u, base_arch_dir, mbox))                

            return threads

            # for u in threads_url_list[0:10]:
            #     print "---------------------------------------"
            #     tt = collect_threads_from_url(u, base_arch_dir, mbox)
            #     threads.append(tt)
                

    return None

def collect_threads_from_url(url, base_arch_dir, mbox):

    response = urllib.request.urlopen(url)
    html = response.read().decode(encoding="utf-8")
    soup = BeautifulSoup(html, "html5lib")

    # base url 
    base_url = url

    # collect name
    threads_name = soup.select('p:nth-of-type(1) title')[0].string
    threads_name = threads_name.replace(' ', '_')

    # thread data struct
    threads = {'name' : threads_name, 'url' : base_url, 'threads' : []}

    logging.info("Collecting Threads of: " + threads_name)

    # check if archive already exists
    file_path = os.path.join(base_arch_dir, threads['name'] + ".json")
    if os.path.isfile(file_path):
        logging.info("archive already exists. loading from file " + file_path)
        with open(file_path, 'r') as fpin:
            threads = json.load(fpin)
    else:
        lists = soup.select('ul:nth-of-type(1) > li')

        nbr_threads = str(len(lists))
        n = 0

        for l in lists:
            n += 1
            logging.info("> " + str(n) + " / " + nbr_threads)

            try:
                thread = archive_thread(l, base_url, None)
                threads['threads'].append(thread)
            except:
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                del tb                
                continue

            time.sleep(DELAY)

        # write 
        logging.info("writing archive to file " + file_path)

        with open(file_path, 'w') as fp:
            json.dump(threads, fp, indent=4)

        logging.info("done. ")

    return threads

    

def archive_thread(li, base_url, parent_thread_data):

	thread_link = li.select('strong a')[0]
	thread_url = urlparse.urljoin(base_url, thread_link.get('href'))
	thread_id = thread_link.get('name')
	thread_title = thread_link.string
	thread_author_name = li.select('em')[0].string

	message = {u'id': thread_id, u'subject': thread_title, u'url': thread_url, u'author_name': thread_author_name}

	collect_message(thread_url, message)

	follow = li.select('ul > li')
	if len(follow) > 0:
		for f in follow:
			follow_link = f.select('strong a')
			if len (follow_link) > 0:
				archive_thread(f, base_url, message)  ## recursion
	
	if parent_thread_data is None:
		return message

	if u'follow-up' not in parent_thread_data:
		parent_thread_data[u'follow-up'] = []

	parent_thread_data[u'follow-up'].append(message)

	return message


def collect_message(url, message):

    response = urllib.request.urlopen(url)
    html = response.read().decode(encoding="utf-8")
    soup = BeautifulSoup(html, "html5lib")    

    #note: this should follow an RFC header standard -- MHonArc has header info in the 1th <pre>

    message_labels = ('to', 'subject', 'from', 'date', 'message-id', 'content-type')    

    # mhonarc xcomments
    # ref: http://www.schlaubert.de/MHonArc/doc/resources/printxcomments.html
    message['subject'] = parse_xcomment(soup, "X-Subject")
    message['date'] = parse_xcomment(soup, "X-Date")
    message['from'] = parse_xcomment(soup, "X-From-R13") #useless...
    message['message-id'] = parse_xcomment(soup, 'X-Message-Id')
    message['content-type'] = parse_xcomment(soup, 'X-Content-Type')

    # parse what is displayed on the page

    info = soup.select('ul:nth-of-type(1) > li')

    for i in info:
        if i.em == None:
            continue
        field = i.em.string
        if field.lower() in message_labels:
        	message[field.lower()] = i.text.strip(field + ": ")

    ## reformat from -- [author_name, email_addr]

    # from_addr = email.utils.parseaddr(message['from'])
    # message['author_name'] = from_addr[0]
    # message['from'] = from_addr[1]

    ## -- content --
    # test
    c1 = soup.select('pre:nth-of-type(1)')
    if len(c1) > 0:
        message['content'] = c1[0].text
    else:
        message['content'] = soup.select('pre:nth-of-type(2)')[0].text

# mhonarc xcomments
# ref: http://www.schlaubert.de/MHonArc/doc/resources/printxcomments.html
def parse_xcomment(soup, xcom):
    com = soup.find(text=re.compile(xcom))
    if com is not None:
        return com.strip('<!-- ').strip(' -->').strip(xcom + ":").strip()
    return com

def test_xcomment(soup):
    return soup.find(text=re.compile('X-Message-Id')) is not None
