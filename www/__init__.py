from flask import Flask

app = Flask(__name__)

from www import routes
from www import config

# import logging
# logging.basicConfig(level=logging.DEBUG)

# from www import archives