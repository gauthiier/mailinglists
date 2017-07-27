from flask import Flask

app = Flask(__name__)

from www import routes

# import logging
# logging.basicConfig(level=logging.DEBUG)

# from www import archives