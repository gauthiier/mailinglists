from flask import render_template
from www import app
from www import archives
from datetime import datetime

@app.route('/')
def index():
	k = archives.archives_data.keys()
	return render_template("index.html", archives=k)

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

	return None

@app.route('/<list>')
def get_list(list):
	if list in archives.archives_data:
		d = []
		for k, v in sorted(archives.archives_data[list].items(), key=get_key, reverse=True):
			d.append({"name": k, "url": v['url'], "nbr_threads": len(v['threads'])})
		return render_template("list.html", list_name=list, list=d)

	else:
		return 'nee nee'

@app.route('/<list>/<sublist>')
def get_sublist(list, sublist):

	sublist = sublist.replace(' ', '_')
	if list in archives.archives_data and sublist in archives.archives_data[list]:
		return render_template("threads.html", sublist_name=sublist, threads=archives.archives_data[list][sublist]['threads'])
	else:
		return 'na na'

@app.route('/<list>/<sublist>/<int:index>')
def get_message(list, sublist, index):

	sublist = sublist.replace(' ', '_')
	index = int(index)
	if list in archives.archives_data and sublist in archives.archives_data[list] and index < len(archives.archives_data[list][sublist]['threads']):
		return render_template("message.html", message=archives.archives_data[list][sublist]['threads'][index])
	else:
		'non non'

@app.route('/<list>/<sublist>/<int:index>/<path:follow_ups>')
def get_follow_ups(list, sublist, index, follow_ups):

	sublist = sublist.replace(' ', '_')
	index = int(index)

	ups = follow_ups.split('/')
	follow = []
	for u in ups:
		follow.append(int(u))

	if list in archives.archives_data and sublist in archives.archives_data[list] and index < len(archives.archives_data[list][sublist]['threads']):
		message = archives.archives_data[list][sublist]['threads'][index]
		for f in follow:
			message = message['follow-up'][f]
		return render_template("message.html", message=message)
	else:
		'nope nope'









