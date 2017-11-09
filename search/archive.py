import logging, os, json, re
from datetime import datetime

class Archive():

	def __init__(self, archives_dir=None):
		if archives_dir==None:
			from www import config
			self.archives_dir = config.ARCHIVES_PATH
		else:
			self.archives_dir = archives_dir

		self.loaded = False

	def load(self, archive_name=None):

		if archive_name == None:
			raise Exception('Archive is not specified')

		archive_path = os.path.join(self.archives_dir, archive_name)
		if not os.path.isdir(archive_path):
			raise Exception('Archive ' + path + ' does not exist')

		self.archive_name = archive_name
		self.archive_path = archive_path

		files = [f for f in os.listdir(archive_path) if f.endswith('.json')]

		self.archive = {}

		for f in files:
			file_path = os.path.join(archive_path, f)
			label = f.replace('.json', '')
			with open(file_path) as fdata:
				self.archive[label] = json.load(fdata)	

		self.loaded = True		

	def search_message(self, keyword, msg, index_str, results, field='content'):

		nbr_hits = 0
		if msg[field] is not None and msg[field].lower().find(keyword.lower()) > 0:
			nbr_hits += 1
			results.append({ "index_str": index_str, "subject": msg['subject'], "date": msg['date'], "author_name": msg['author_name'], "url": msg['url'] })

		if 'follow-up' in msg:
			i = 0
			for m in msg['follow-up']:
				current_index_str = index_str + '/' + str(i)
				nbr_hits += self.search_message(keyword, m, current_index_str, results, field)
				i += 1

		return nbr_hits


	def search(self, keyword, field='content', min_hits=0):

		search_results = { "keyword": keyword, "field": field, "archive": self.archive_name, "results": [] }

		for k, v in sorted(self.archive.items(), key=get_key, reverse=True):

			current_index_str = self.archive_name + '/' + k
			hits = []
			nbr_hits = 0
			i = 0
			for m in v['threads']:
				current_index_str = self.archive_name + '/' + k + '/' + str(i)
				nbr_hits += self.search_message(keyword, m, current_index_str, hits, field)
				i += 1

			if nbr_hits > min_hits:
				# nettime-l - fix (the name of the thread from ex. 'nettime-l_Jan_01' to 'January 2001')
				if k.startswith("nettime-l_"):
					dt = datetime.strptime(k, "nettime-l_%b_%y")
					k = dt.strftime("%B_%Y")
				search_results['results'].append({ 'thread': k, 'nbr_hits': nbr_hits, 'hits': hits})

		return search_results


				
def get_key(kv_tuple):

	k = kv_tuple[0]	

	# k is of the form "Month_Year" - ex.: "January_2001"
	try:
		return datetime.strptime(k, "%B_%Y")
	except Exception:
		pass

	# k is of the form "Month(abv)_Year(abv)" - ex.: "Jan_01"
	try:
		return datetime.strptime(k, "%b_%y")
	except Exception:
		pass

	# k is of the form "Year" - ex.: "2001"
	try:
		return datetime.strptime(k, "%Y")
	except Exception:
		pass

	# nettime-l - fix - k is of the form "nettime-l_Month(abv)_Year(abv)" - ex.: "nettime-l_Jan_01"
	try:
		return datetime.strptime(k, "nettime-l_%b_%y")
	except Exception:
		pass

	print("--------------")
	print(k)

	return None





