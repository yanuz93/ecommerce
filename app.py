from flask import Flask, request
from flask_restful import Api
import sys
import logging
from logging.handlers import RotatingFileHandler as RFH
from werkzeug.contrib.cache import SimpleCache

cache = SimpleCache()
##########################################
# Import Blueprints below
##########################################
from blueprints import app, manager

api = Api(app, catch_all_404s=True)

if __name__ == '__main__':
    try:
        if sys.argv[1] == 'db':
            manager.run()
    except Exception as excpt:
        formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
        log_handler = RFH('%s/%s' % (app.root_path, 'storage/log/error.log'),maxBytes=1000000,backupCount=10)
        log_handler.setLevel(logging.ERROR)
        log_handler.setFormatter(formatter)
        app.logger.addHandler(log_handler)

    app.run(debug=True, host='0.0.0.0', port='8888')
