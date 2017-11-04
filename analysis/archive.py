import numpy as np
import pandas as pd
import email, email.parser
import os, datetime, json, gzip, re
import analysis.util
import analysis.query


def filter_date(msg, archive_name):
	
	time_tz = analysis.util.format_date(msg, archive_name)
	if not time_tz:
		return None

	dt = datetime.datetime.fromtimestamp(time_tz)
	try:
		date_time = pd.to_datetime(dt)
	except pd.tslib.OutOfBoundsDatetime:
		print('time out of bound')
		print(dt)
		return None

	min_date = pd.to_datetime(analysis.util.min_date(archive_name), format='%d/%m/%Y')
	max_date = pd.to_datetime(datetime.datetime.now())
	if date_time < min_date or date_time > max_date:
		return None

	return date_time


def message_to_tuple_record(msg, records, archive_name, references='X'):

	# check date first?
	date = filter_date(msg, archive_name)
	if not date:
		print("Archive::filter_date returned None. Skip.")
		return

	# check / filter from email address second?
	from_addr = analysis.util.format_from(msg, archive_name)
	if not from_addr:
		print("Archive::analysis.util.format_from returned None. Skip.")
		return

	url = analysis.util.format_url(msg, archive_name)
	author = analysis.util.format_author(msg, archive_name)
	subject = analysis.util.format_subject(msg, archive_name)
	message_id = analysis.util.format_id(msg, archive_name)
	content = analysis.util.format_content(msg, archive_name)

	records.append((message_id,
						from_addr,
						author,
						subject,
						date,
						url,
						len(content),
						0 if not 'follow-up' in msg else len(msg['follow-up']),
						references))

	# recursive follow up -- but references is not keeping track really...
	if 'follow-up' in msg:
		for f in msg['follow-up']:
			message_to_tuple_record(f, records, archive_name, references=message_id)

	return 

def json_data_to_pd_dataframe(json_data, archive_name):

	records = []
	for d in json_data:
		for dd in d['threads']:
			message_to_tuple_record(dd, records, archive_name)

	print('zzzzzzzzz ----> ' + archive_name + " ---- " + str(len(records)))

	df = pd.DataFrame.from_records(records,
						index='date',
						columns=['message-id',
									'from',
									'author',
									'subject',
									'date',
									'url',
									'content-length',
									'nbr-references',
									'references'])

	df.index.name = 'date'

	return df

def load_from_file(filename, archive_name, archive_dir, json_data=None):

	if not filename.endswith('.json.gz'):
		file_path = os.path.join(archive_dir, filename + '.json.gz')
	else:
		file_path = os.path.join(archive_dir, filename)

	if os.path.isfile(file_path):
		with gzip.open(file_path, 'r') as fp:
			json_data = json.load(fp)
			return json_data_to_pd_dataframe(json_data['threads'], archive_name)
	else:
		#list of all "filename[...].json.gz" in archive_dir
		files = sorted([f for f in os.listdir(archive_dir) if os.path.isfile(os.path.join(archive_dir, f)) and f.startswith(filename) and f.endswith('.json.gz')])
		if files:
			filename = files[-1] # take the most recent (listed alpha-chronological)
			file_path = os.path.join(archive_dir, filename)
			if os.path.isfile(file_path):
				with gzip.open(file_path, 'r') as fp:
					json_data = json.load(fp)
					return json_data_to_pd_dataframe(json_data['threads'], archive_name)
		else:
			#list of all json files in archive_dir/filename
			dir_path = os.path.join(archive_dir, filename)
			if not os.path.isdir(dir_path):
				return None

			files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.endswith('.json')]
			if not files:
				return None

			# load all json files
			threads = []
			for file_path in files:
				with open(file_path, 'r') as fp:
					json_data = json.load(fp)
					threads.append(json_data)

			print('---> ' + archive_name)
			return json_data_to_pd_dataframe(threads, archive_name)
				

class Archive:

	data = None				# "raw" json data
	dataframe = None 		# main pd dataframe

	def __init__(self, archive_name, archive_dir="archives"):

		if isinstance(archive_name, pd.core.frame.DataFrame):
			self.dataframe = archive_name.copy()

		if isinstance(archive_name, str):
			# need a filename or a dir name....
			self.dataframe = load_from_file(archive_name, archive_name, archive_dir, self.data)

	def query(self):
		q = analysis.query.Query(self)
		return q

