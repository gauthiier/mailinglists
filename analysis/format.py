import analysis.query
import logging, html, numpy
from tabulate import tabulate

def makeurl(text, url):
	return '<a href="' + url + '">' + text + "</a>"

def table_threads_ranking(ranking_dataframe):

	html_str = '<table class="threads_ranking">'


	html_str += '<tr>'
	html_str += '<td class="td_date_t">date</td>'
	html_str += '<td class="td_subject_t">subject</td>'
	html_str += '<td class="td_from_t">from</td>'
	html_str += '<td class="td_rep_t">replies</td>'
	html_str += '</tr>'


	for i, row in ranking_dataframe.iterrows():

		html_str += '<tr>'
		html_str += '<td class="td_date">' + str(i) + '</td>'
		html_str += '<td class="td_subject">' + makeurl(row['subject'], row['url']) + '</td>'
		html_str += '<td class="td_from">' + row['from'] + '</td>'
		html_str += '<td class="td_rep">' + str(row['nbr-references']) + '</td>'
		html_str += '</tr>'

	html_str += "</table>"

	return html_str

def frame_to_dictionary_threads_ranking(ranking_dataframe):

	results = []
	for i, row in ranking_dataframe.iterrows():
		d = {'date': str(i), 'subject': row['subject'], 'url': row['url'], 'from': row['from'], 'nbr-references': row['nbr-references']}
		results.append(d)
	return results



class Html:

	query = None

	def __init__(self, q=None):

		if not isinstance(q, query.Query):
			logging.error("HtmlFormat constructor Error: query must be of type nettime.query.Query")
			raise Exception()

		self.query = q

	def threads_ranking(self, rank=5, resolution=None):
		
		data = self.query.threads_ranking(rank=rank)

		h = html.HTML()
		t = h.table()

		r = t.tr
		r.td('date', klass='td_date_t')
		r.td('from', klass='td_from_t')
		r.td('replies', klass='td_rep_t')
		r.td('subject', klass='td_subject_t')

		for i, row in data.iterrows():
			r = t.tr

			print(row.index)

			r.td(str(row['date']), klass='td_date')
			r.td(row['from'], klass='td_from')
			r.td(str(row['nbr-references']), klass='td_rep')
			r.td('', klass='td_subject').text(str(h.a(row['subject'], href=row['url'])), escape=False)

		return str(t)

	@staticmethod
	def from_dataframe(data_frame, table_name=None, name_map={}, url_map={}):

		header = []
		if data_frame.index.name in name_map:
			header.append(name_map[data_frame.index.name])
		else:
			header.append(data_frame.index.name)
		for h in data_frame.columns:
			if h in name_map:
				h = name_map[h]
			header.append(h)

		css_header = []
		css_element = []
		for i in header:
			css_header.append('td_' + i + '_t')
			css_element.append('td_' + i)

		h = html.HTML()
		if table_name:
			t = h.table(id=table_name, klass=table_name + '_t')
		else:
			t = h.table()

		# url map
		url_hash = {}
		url_skip = []
		url_keys = url_map.keys()
		for u in url_keys:
			 if u in header and url_map[u] in header:
			 	url_indx = header.index(url_map[u])
			 	url_hash[header.index(u)] = url_indx
			 	url_skip.append(url_indx)
			 	header.pop(url_indx)

		#header
		r = t.tr
		n = 0
		for j in header:
			r.td(str(j), klass=css_header[n])
			n += 1

		
		#elements		
		for k, row in data_frame.iterrows():
			r = t.tr
			r.td(str(k), klass=css_element[0])
			n = 1
			for l in row:

				if n in url_skip:
					continue

				if isinstance(l, float): 
					if l % 1 > 0:
						l = '{0:.4f}'.format(l)
					else:
						l = int(l)

				if n in url_hash.keys():
					url = row[url_hash[n] - 1]
					r.td('', klass=css_element[n]).text(str(h.a(str(l), href=url)), escape=False)

				else:
					r.td(str(l), klass=css_element[n])
				n += 1

		return str(t)

class Tab:

	@staticmethod
	def from_dataframe(data_frame, name_map={}, format=".0f"):

		header = []
		header.append(data_frame.index.name)
		for h in data_frame.columns:
			if h in name_map:
				h = name_map[h]
			header.append(h)

		return tabulate(data_frame, headers=header, floatfmt=format)


