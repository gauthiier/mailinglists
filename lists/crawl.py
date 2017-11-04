from urllib.parse import urlparse
import lists.pipermail as pipermail
import lists.listserv as listserv
import lists.mhonarc as mhonarc
import lists.mhonarc_nettime as mhonarc_nettime

DELAY = 0.2

def crawl(url, name, sublist_name=None, archive_dir="archives"):
	u = urlparse(url)

	# the following type 'tests' are very weak...
	# how to test is list is pipermail / listserv / mhonarc?

	if 'pipermail' in u.path:
		# if no name, get the trailing path element (re: /pipermail/xyz -- 'xyz')
		if name is None:
			path = u.path if not u.path.endswith('/') else u.path[:len(u.path) - 1]
			name = path.strip().split('/')[-1]

		pipermail.collect_from_url(url, name, archive_dir)
			
	elif 'cgi-bin' in u.path:
		listserv.collect_from_url(url, name, archive_dir)

	# special case -- nettime.
	# the name should be the sublist_name (i.e nettime-l)
	elif "nettime" in name:
		mhonarc_nettime.collect_from_url(url, name, name, archive_dir)

	else:
		print('mhonarc?')

	return