import os

# matplot view/windows
import matplotlib
matplotlib.interactive(True)

# pd display
import pandas as pd
pd.set_option('display.max_colwidth', 100)

from analysis.archive import Archive
from analysis.query import Query
from analysis.plot import Plot

import analysis.format

# spectre: slategrey
# nettime: red
# crumb: purple
# empyre: darkblue

def save_fig_cohort(q, name, dir, color):
	t = name + " - Cohorts"	
	pp = q.cohort().plot(color=color, title=t)
	ts = name + "_cohorts.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_messages_total(q, name, dir, color):
	t = name + " - Nbr. Messages"	
	pp = q.activity_overall().plot(kind='bar', color=color, title=t)
	ts = name + "_messages.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_threads_total(q, name, dir, color):
	t = name + " - Nbr. Threads"	
	pp = q.threads_overall().plot(kind='bar', color=color, title=t)
	ts = name + "_threads.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_messages_constituency(q, name, dir):
	t = name + " - Messages Constituency"
	replies = pd.Series(q.replies_overall(series=True))
	# threads = pd.Series(q.single_threads_overall(series=True))
	threads = pd.Series(q.threads_overall(series=True))
	messages = pd.Series(q.activity_overall(series=True))
	single_messages = messages - (replies + threads)

	# df = {'a': single_messages, 'b': threads, 'c': replies}
	# df = pd.DataFrame([single_messages, threads, replies], columns=['a', 'b', 'c'])
	df = pd.concat([single_messages.to_frame('single-messages').astype(int), threads.to_frame('threads').astype(int), replies.to_frame('replies').astype(int)], axis=1)
	pp = df.plot(kind='bar', stacked=True, title=t)

	# pp = [single_messages, threads, replies].plot(kind='bar', stacked=True)

	ts = name + "_constituency.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_avg_threads_replies(q, name, dir, color):
	t = name + " - Avg. Threads + Replies"
	replies = pd.Series(q.replies_overall(series=True))
	threads = pd.Series(q.threads_overall(series=True))
	messages = pd.Series(q.activity_overall(series=True))

	avg_threads_messages = (replies + threads) / messages

	pp = pd.DataFrame(avg_threads_messages).plot(kind='bar', color=color, title=t)

	ts = name + "_avg_threads_replies.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_diff_threads_replies_vs_messages(q, name, dir, color):
	t = name + " - Diff. Threads + Replies vs Single Messages"
	replies = pd.Series(q.replies_overall(series=True))
	threads = pd.Series(q.threads_overall(series=True))
	rt = replies + threads
	messages = pd.Series(q.activity_overall(series=True))

	diff_threads_messages =  (2 * rt) - messages

	pp = pd.DataFrame(diff_threads_messages).plot(kind='bar', color=color, title=t)

	ts = name + "_diff_threads_replies_messages.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def save_fig_ratio_replies_threads(q, name, dir, color):
	t = name + " - Ratio Replies per Thread"
	replies = pd.Series(q.replies_overall(series=True))
	threads = pd.Series(q.threads_overall(series=True))

	ratio_replies_threads =  replies / threads

	pp = pd.DataFrame(ratio_replies_threads).plot(kind='bar', color=color, title=t)

	ts = name + "_ratio_replies_threads.png"
	filename = os.path.join(dir, ts)
	pp.get_figure().savefig(filename)

def html_td_rank_year(year, data):
	td_str = '<td class="td_list">'
	if year in data:
		td_str += analysis.format.table_threads_ranking(data[year])
	td_str += '</td>'
	return td_str

def html_table_ranking_per_year(ranking_nettime, ranking_crumb, ranking_spectre, ranking_empyre):

	html_str = '<table id="rankings">'

	html_str += '<tr>'
	html_str += '<td class="td_year_t">year</td>'
	html_str += '<td class="td_list_t">nettime</td>'
	html_str += '<td class="td_list_t">crumb</td>'
	html_str += '<td class="td_list_t">spectre</td>'
	html_str += '<td class="td_list_t">empyre</td>'
	html_str += '</tr>'

	years = sorted(ranking_nettime.keys())

	print(years)

	for i in years:
		html_str += '<tr>'
		html_str += '<td class="td_list">' + i + '</td>'
		html_str += html_td_rank_year(i, ranking_nettime)
		html_str += html_td_rank_year(i, ranking_crumb)
		html_str += html_td_rank_year(i, ranking_spectre)
		html_str += html_td_rank_year(i, ranking_empyre)
		html_str += '</tr>'

	html_str += '</table>'
	return html_str


print("nettime")
#nettime
nt = Archive('nettime-l')
ntq = nt.query()
ntp = Plot(ntq)



# save_fig_cohort(ntq, 'nettime', 'figs/', 'red')
# save_fig_messages_total(ntq, 'nettime', 'figs/', 'red')
# save_fig_threads_total(ntq, 'nettime', 'figs/', 'red')
# save_fig_messages_constituency(ntq, 'nettime', 'figs/')

# save_fig_avg_threads_replies(ntq, 'nettime', 'figs/', 'red')
# save_fig_diff_threads_replies_vs_messages(ntq, 'nettime', 'figs/', 'red')
# save_fig_ratio_replies_threads(ntq, 'nettime', 'figs/', 'red')

ranking_nettime = ntq.threads_ranking(rank=15)

# print(r['2000'])

# print(analysis.format.table_threads_ranking(r['2000']))


print("crumb")
#crumb
cr = Archive('crumb')
crq = cr.query()
crp = Plot(crq)

# save_fig_cohort(crq, 'crumb', 'figs/', 'purple')
# save_fig_messages_total(crq, 'crumb', 'figs/', 'purple')
# save_fig_threads_total(crq, 'crumb', 'figs/', 'purple')
# save_fig_messages_constituency(crq, 'crumb', 'figs/')

# save_fig_avg_threads_replies(crq, 'crumb', 'figs/', 'purple')
# save_fig_diff_threads_replies_vs_messages(crq, 'crumb', 'figs/', 'purple')
# save_fig_ratio_replies_threads(crq, 'crumb', 'figs/', 'purple')

ranking_crumb = crq.threads_ranking(rank=15)


print("empyre")
#empyre
em = Archive('empyre')
emq = em.query()
emp = Plot(emq)

# save_fig_cohort(emq, 'empyre', 'figs/', 'darkblue')
# save_fig_messages_total(emq, 'empyre', 'figs/', 'darkblue')
# save_fig_threads_total(emq, 'empyre', 'figs/', 'darkblue')
# save_fig_messages_constituency(emq, 'empyre', 'figs/')

# save_fig_avg_threads_replies(emq, 'empyre', 'figs/', 'darkblue')
# save_fig_diff_threads_replies_vs_messages(emq, 'empyre', 'figs/', 'darkblue')
# save_fig_ratio_replies_threads(emq, 'empyre', 'figs/', 'darkblue')

ranking_empyre = emq.threads_ranking(rank=15)

print("spectre")
#spectre
sp = Archive('spectre')
spq = sp.query()
spp = Plot(spq)

# save_fig_cohort(spq, 'spectre', 'figs/', 'slategrey')
# save_fig_messages_total(spq, 'spectre', 'figs/', 'slategrey')
# save_fig_threads_total(spq, 'spectre', 'figs/', 'slategrey')
# save_fig_messages_constituency(spq, 'spectre', 'figs/')

# save_fig_avg_threads_replies(spq, 'spectre', 'figs/', 'slategrey')
# save_fig_diff_threads_replies_vs_messages(spq, 'spectre', 'figs/', 'slategrey')
# save_fig_ratio_replies_threads(spq, 'spectre', 'figs/', 'slategrey')

ranking_spectre = spq.threads_ranking(rank=15)


## comparative ranking

rankings = html_table_ranking_per_year(ranking_nettime, ranking_crumb, ranking_spectre, ranking_empyre)

html_template = 'figs/ranking/index_template.html'
with open(html_template, 'r') as fp:
	h = fp.read()

html = h.replace("--table--", rankings)

html_output = 'figs/ranking/index.html'
with open(html_output, 'w+') as fp:
	fp.write(html)

