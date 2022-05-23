# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
import sys
import logging 
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
	datefmt='%Y-%m-%d:%H:%M:%S',
	level=logging.INFO) 
logger = logging.getLogger(__name__)

import os
import traceback
from flask import Flask, request, redirect, render_template, Response, url_for, flash, abort

# *** Uncomment to use taskqueue ***
# from google.cloud import tasks_v2
# taskClient = tasks_v2.CloudTasksClient()

# *** Uncomment to use ndb ***
# from google.cloud import ndb
# ndbClient = ndb.Client()

# # https://cloud.google.com/appengine/docs/standard/python/migrate-to-python3/migrate-to-cloud-ndb#using_a_runtime_context_with_wsgi_frameworks
# def ndb_wsgi_middleware(wsgi_app):
# 	def middleware(environ, start_response):
# 		with ndbClient.context():
# 			return wsgi_app(environ, start_response)

# 	return middleware



def create_app():
	app = Flask(__name__)
	app.secret_key = '0909090909' # Generate your own random key for use as the app's secret key 
	# *** Uncomment to use ndb ***
	# app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)  # Wrap the app in middleware.


	@app.route("/")
	def index():
		params = {"message": "Hello World"}
		return render_template("index.htm", **params)
		

	@app.errorhandler(404)
	def page_not_found(e):
		return render_template("404.htm"), 404


	return app