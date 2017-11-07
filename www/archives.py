import logging, os, json

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logging.info('**** new Singleton instance')
        return cls._instances[cls]

class Archives(metaclass=Singleton):

	def __init__(self, archives_dir=None):

		if archives_dir==None:
			from www import config
			self.archives_dir = config.ARCHIVES_PATH
		else:
			self.archives_dir = archives_dir

		self.data = {}
		self.loaded = False

		logging.info('loading archives...')

		self.load()

		logging.info('done.')

	def load(self):

		if self.loaded:
			return

		if not os.path.isdir(self.archives_dir):
			logging.error("Archives:: the path - " + self.archives_dir + " - is not a valid directory. Aborting.")
			logging.error(" -- current cwd is: " + os.getcwd())

			return

		arch = [d for d in os.listdir(self.archives_dir) if os.path.isdir(os.path.join(self.archives_dir, d))]

		self.data = {}
		for a in arch:

			logging.info("loading " + a)

			archive_path = os.path.join(self.archives_dir, a)
			self.data[a] = self.load_archive(archive_path)

			logging.info("done.")

		self.loaded = True
		

	def load_archive(self, archive_dir):

		if not os.path.isdir(archive_dir):
			logging.error("Archives:: the path - " + archive_dir + " - is not a valid directory. Aborting.")
			return

		files = [f for f in os.listdir(archive_dir) if f.endswith('.json')]

		arch = {}
		for f in files:
			file_path = os.path.join(archive_dir, f)
			with open(file_path) as fdata:
				arch[f.replace('.json', '')] = json.load(fdata)

		return arch	



