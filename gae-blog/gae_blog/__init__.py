# Copyright 2022 NoCommandLine
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

import sys
import logging 
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
	datefmt='%Y-%m-%d:%H:%M:%S',
	level=logging.INFO) 
logger = logging.getLogger(__name__)

import os
import traceback
from flask import Flask, request, redirect, render_template, Response, url_for, flash, abort
from gae_blog.models.models import BlogPosts, Comments 
from collections import defaultdict, OrderedDict
from slugify import slugify
from html.parser import HTMLParser
from html import unescape
import re
import datetime


# https://cloud.google.com/appengine/docs/standard/python3/testing-and-deploying-your-app#detecting_application_runtime_environment
# if not os.getenv('GAE_ENV', '').startswith('standard'):
# 	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service_account/nytcomments-c66069beedaf.json"

from google.cloud import ndb
ndbClient = ndb.Client()



MONTH_NAME = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September',
		10:'October', 11:'November', 12:'December'}


# # https://cloud.google.com/appengine/docs/standard/python/migrate-to-python3/migrate-to-cloud-ndb#using_a_runtime_context_with_wsgi_frameworks
def ndb_wsgi_middleware(wsgi_app):
	def middleware(environ, start_response):
		with ndbClient.context():
			return wsgi_app(environ, start_response)

	return middleware



def byDate():
	return defaultdict(int)



# We need to strip out any HTML tags before creating the snippet
class MLStripper(HTMLParser):
	def __init__(self):
		#Since Python 3, we need to call the __init__() function 
		#of the parent class
		super().__init__()
		self.reset()
		self.fed = []
		
	
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)


# Now create a snippet. 
# This code was sourced from - http://rabexc.org/posts/html-snippets-in-python
# We then modified it so that the snippet returned ends in a complete word
# e.g. Starbucks logo... instead of Starbucks lo...
def createSnippet(text, limit=150):
	s = MLStripper()
	s.feed(unescape(text))
	#s.feed(text)
	
	fullText = s.get_data()

	# Retrieve the first 150 characters of the input text
	snippet = fullText[0:limit]
 
	# Now go through this first 150 characters and make sure it ends in a full word
	regexPattern = r'^{0}.*?\b'.format(snippet.encode("utf-8"))
	newSnippet = re.search(regexPattern, fullText, re.I|re.M)
	if newSnippet:
		snippet = newSnippet.group(0).rstrip() 
	
	# If the length of the input text is more than the length of our snippet, append ellipsis '...' to it
	if len(text) > limit:
		snippet += "..."

	return snippet


def processPosts(blogPosts):
	archives = defaultdict(byDate)

	# Create snippet for each post
	# And group publish dates of the posts by month and year
	for i in range(len(blogPosts)):
		blogPosts[i].snippet = createSnippet(blogPosts[i].body) 
		archives[blogPosts[i].publishDate.year][blogPosts[i].publishDate.month] += 1

	return blogPosts, archives


def create_app():
	app = Flask(__name__)
	app.secret_key = 'VLLdltNJ9G8mThlB3' # Generate your own random key for use as the app's secret key 
	# Wrap the app in middleware.
	app.wsgi_app = ndb_wsgi_middleware(app.wsgi_app)  

	
	@app.route("/admin/")
	def adminHandler():
		params = {}

		# Get all blog posts and order them from most recently modified
		blogPosts = BlogPosts.query().order(-BlogPosts.lastModified).fetch()
		if blogPosts:
			params["blogPosts"] = blogPosts
			
		return render_template("admin.htm", **params)

		

	@app.route("/admin/post/<action>/", methods = ["GET", "POST"])
	@app.route("/admin/post/<action>/<id>/", methods = ["GET", "POST"])
	def createEditHandler(action="create", id=None):
		# If this is a new blog post, set the 'isDraft' property to true
		if action == "create":
			blogPost = {"isDraft":True}
			params = {"blogPost" : blogPost}
			return render_template("newPost.htm", **params) 

		# If user wants to update an existing blog post (this means an id must have been provided)
		# Retrieve the post
		elif action == "edit" and id is not None:
			id = int(id)
			blogPost = BlogPosts.get_by_id(id)
			if not blogPost:
				abort(404)
			else:
				params = {"blogPost"  : blogPost}
				return render_template("newPost.htm", **params)

		# If user wants to save a post (which means they submitted the form,
		# hence request.method == "POST")
		elif action == "save" and request.method == "POST":
			# Get the data from the UI
			title = request.values.get("title")
			body =  request.values.get("blogPostBody")
			seo_keywords =  request.values.get("seo_keywords")
			draft =  request.values.get("draft")
			image_url =  request.values.get("imageURL")
			image_title =  request.values.get("imageTitle")
			saveAndClose = request.values.get("saveClose", None)
			publishDate = None
			slug = slugify(title)
			
			if id:
				id = int(id)

			if seo_keywords and seo_keywords != "":
				seo_keywords = [t.strip() for t in seo_keywords.split(",")]
			else:
				seo_keywords = []

			if not draft or draft == "on":
				draft = True

			
			# If user clicked the 'publish' button, then isDraft has to be False
			# We should also close the page after publishing			
			publish = request.values.get("publish", None)
			if publish:
				draft = False
				publishDate = datetime.datetime.utcnow()
				saveAndClose = True
			
			blogPost = BlogPosts.get_by_id(id) if id else None			
			if blogPost:
				# It"s an edit of an existing item.
				blogPost.title = title
				blogPost.body = body
				blogPost.isDraft = draft
				blogPost.imageURL = image_url
				blogPost.imageTitle = image_title
				blogPost.seo_keywords = seo_keywords
				blogPost.publishDate = publishDate
				blogPost.slug = slug
				
			else:
				# This is a new blogPost.
				blogPost = BlogPosts(title=title, body=body, isDraft=draft, imageURL=image_url, 
					imageTitle= image_title, seo_keywords=seo_keywords, publishDate=publishDate, slug=slug) 
			
			key = blogPost.put()
			
			
			# If user did not click 'save and close'
			# then reload the contents of the updated post
			if not saveAndClose:
				params = {"blogPost"  : blogPost}
				return render_template("newPost.htm", **params)
			else:
				return redirect("/admin/")


		elif action == "delete":
			id =  request.values.get("id")
			if id:
				id = int(id)
				blogPost = BlogPosts.get_by_id(id)
				if blogPost:
					blogPost.delete()
			else:
				flash("You did not specify a blog post Id")

			redirect("/admin/")

	
	@app.route("/archive/<year>/<month>/")
	@app.route("/archive/<year>/<month>/<page>/")
	def archiveHandler(year, month, page=None):
		if not year or not month:
			abort(404)
		
		params = {}
		
		blogPosts, next_cursor, more = BlogPosts.getPublishedByDate(int(year), int(month), page)
		if blogPosts == 'Error':
			abort(500)
		
		# If there are more pages of results, then set the cursor for the next page
		if more:
			next_cursor = next_cursor.to_websafe_string()
			params["next_page"] = next_cursor

		if blogPosts:
			
			blogPosts, archives = processPosts(blogPosts)
			params["blogPosts"] = blogPosts
			params["archives"] = OrderedDict(sorted(archives.items(), reverse=True))
			params["month"] = MONTH_NAME


		return render_template("index.htm", **params)



	@app.route("/")
	def index():
		params ={}

		# Check if user is trying to retrieve another page of results
		# If no page number is provided, default  it to None 
		next_page = request.args.get('next_page', None)
		blogPosts, next_cursor, more = BlogPosts.getPublished(page=next_page)
		if blogPosts == 'Error':
			abort(500)
		
		# If there are more pages of results, then set the cursor for the next page
		if more:
			next_cursor = next_cursor.to_websafe_string()
			params["next_page"] = next_cursor

		if blogPosts:
			blogPosts, archives = processPosts(blogPosts)
			params["blogPosts"] = blogPosts
			params["archives"] = OrderedDict(sorted(archives.items(), reverse=True))
			params["month"] = MONTH_NAME
			

		return render_template("index.htm", **params)


	
	@app.route("/<slug>/")
	def viewPostHandler(slug):	
		params ={}
		
		# Retrieve the post associated with this slug
		blogPost = BlogPosts.getBySlug(slug) 

		# If we couldn't find any corresponding post, return a 404
		if not blogPost:
			abort (404)

		params["blogPost"] = blogPost

		return render_template("viewPost.htm", **params)
		



	@app.errorhandler(404)
	def page_not_found(e):
		return render_template("404.htm"), 404



	@app.errorhandler(500)
	def server_error(e):
		return "An unknown error occured", 500


	return app