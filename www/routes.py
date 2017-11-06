from flask import render_template, request, jsonify
from www import app
from www import archives
import search.archive
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

	print(list)
	print(sublist)

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

@app.route('/search')
def searh():
	
	if len(request.args) < 1:
		k = archives.archives_data.keys()
		return render_template("search.html", archives=k, fields=['content', 'from(name)', 'from(email)'])

	k_arg = request.args.get('keyword')
	l_arg = request.args.get('list')
	sl_arg = request.args.get('sublist')
	f_arg = request.args.get('field')

	if k_arg is None or k_arg.strip() == '':
		return "no keyword..."

	if l_arg is None:
		return "no list..."
	
	if not (l_arg == "all") and not (l_arg in archives.archives_data):
		return "list '" + l_arg + "' does not exist"

	if sl_arg is not None:
		if not sl_arg in archives.archives_data[l]:
			return "sublist '" + sl_arg + "' does not exist in list '" + l_arg + "'"

	if f_arg == "from(name)":
		f_arg = 'author_name'
	elif f_arg == "from(email)":
		f_arg = 'from'

	lists = []
	if l_arg == "all":
		for k in archives.archives_data.keys():
			lists.append(k)
	else:
		lists.append(l_arg)

	################################
	##
	##	need to cache all the below
	##
	################################

	results = []
	for l in lists:
		# this makes no sense...
		a = search.archive.Archive()
		a.load(l)
		results.append(a.search(keyword=k_arg, field=f_arg))

	## -- sort results?
	search_results = sorted(results, key=get_result_key)

	return jsonify(result=search_results)

def get_result_key(r):
	return r['archive']

	










