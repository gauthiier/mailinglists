import email
import hashlib

def format_content(msg, archive_name):
	return msg['content']

def format_url(msg, archive_name):
	return msg['url']

def format_author(msg, archive_name):
	return msg['author_name']

def format_from_token(from_str, sep):

	fff = from_str

	from_addr = email.utils.parseaddr(from_str)[1]

	fffa = email.utils.parseaddr(from_str)

	if sep not in from_addr:
		tok = from_str.split()
		try:
			at = tok.index(sep)
			from_addr = ''.join([tok[at-1], '{AT}', tok[at+1]])
			if from_addr.startswith('<') or from_addr.endswith('>'):
				from_addr = from_addr.strip('<').strip('>')
		except ValueError:
			print(tok)
			print("error formating 'from' " + from_str + " -- expecting sep: " + sep)
			print("*** " + fff)
			print("+++")
			print(fffa)
			print("----")

			return None
	else:
		from_addr = from_addr.replace(sep, '{AT}')
	return from_addr.lower()

def format_from(msg, archive_name):
	from_str = msg['from']	

	if " {AT} " in from_str:
		return format_from_token(from_str, '{AT}')
	elif " at " in from_str:
		return format_from_token(from_str, 'at')
	elif "@" in from_str:
		return format_from_token(from_str, '@')
	else:
		return from_str

# returns utc timestamp
def format_date(msg, archive_name):
	date_str = msg['date']
	time_tz = None
	try:
		date_tz = email.utils.parsedate_tz(date_str)
		time_tz = email.utils.mktime_tz(date_tz) #utc timestamp
	except TypeError:
		print("Format Date TypeError")
		print("  > " + date_str)
		return None
	except ValueError:
		print("Format Date ValueError")
		print("  > " + date_str)
		return None
	finally:
		return time_tz

def format_subject(msg, archive_name):
	return msg['subject']

def format_id(msg, archive_name):
	if "message-id" in msg:
		return msg['message-id']
	else:
		# create hash with author_name + date
		s = msg['author_name'] + msg['date']
		sha = hashlib.sha1(s.encode('utf-8'))
		return sha.hexdigest()

# format='%d/%m/%Y'
def min_date(archive_name):
	if "nettime" in archive_name:
		return '01/10/1995'
	elif archive_name == "spectre":
		return '01/08/2001'
	elif archive_name == "empyre":
		return '01/01/2002'
	elif archive_name == "crumb":
		return '01/02/2001'
