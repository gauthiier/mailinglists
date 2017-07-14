from urllib.parse import urlparse
import lists.pipermail as pipermail

DELAY = 0.2

def crawl(url, name, archive_dir):
	u = urlparse(url)

	if 'pipermail' in u.path:
		# if no name, get the trailing path element (re: /pipermail/xyz -- 'xyz')
		if name is None:
			path = u.path if not u.path.endswith('/') else u.path[:len(u.path) - 1]
			name = path.strip().split('/')[-1]

		pipermail.collect_from_url(url, name, archive_dir)
			
	else:
		print('mhonarc?')

	
	return