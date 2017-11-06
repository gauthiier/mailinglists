from flask import Flask

app = Flask(__name__)

from www import routes
from www import config

app.run(debug=True, use_reloader=False)

# import logging
# logging.basicConfig(level=logging.DEBUG)

# from www import archives