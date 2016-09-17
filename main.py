import logging,os

from flask import Flask,redirect, Response

import cloudstorage as gcs
from config import bucket_name

app = Flask(__name__)



@app.route('/datamachina')
def datamachina():
	#return redirect("http://bit.ly/rssdatamachina", code=302) #public share not working
	filename="/"+bucket_name+"/data/datamachina.rss"
	gcs_file = gcs.open(filename)
	content = gcs_file.read()
	gcs_file.close()
	return Response(content, mimetype='application/rss+xml')

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500