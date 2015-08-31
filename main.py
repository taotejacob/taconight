#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#

import os
import jinja2
import webapp2

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)



########################################3
##
##
## Databases
##
##
########################################3

#create database for weekly standings
class Event(ndb.Model):
	date = ndb.DateTimeProperty()
	location = ndb.StringProperty()
	attendees = ndb.StringProperty()
	completed = ndb.IntegerProperty()
	messages = ndb.TextProperty()
	max_invite = ndb.IntegerProperty()
	host = ndb.StringProperty()

#create users database:
class Account(ndb.Model):
	username = ndb.StringProperty()
	email = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	first_last = ndb.StringProperty()
	diet_info = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add = True)
	attendance = ndb.IntegerProperty()



#####################################
##
##  Webpage handlers
##
#####################################



class PublicHome(Handler):
	def get(self):
		self.render('publichome.html')

class Rsvp(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q < 1:
			self.redirect('/auth/signup')

		self.render('rsvp.html',
			user_name = user_name)



def inputUserData(email, first_name, last_name, user_name, diet_info):
	p = Account(username = user_name.nickname(),
				#userid = user_name.user_id(),
				email = user_name.email(),
				first_name = first_name,
				last_name = last_name,
				first_last = first_name + " " + last_name[0],
				attendance = 0,
				diet_info = "Vegan:0, Vegitarian:0, Kosher:0"
				)
	p.put()




class SignUp(Handler):
	def get(self):
		self.render('signup.html')

	def post(self):
		user_name = users.get_current_user()
		first_name = self.request.get('first_name')
		last_name = self.request.get('last_name')
		diet_info = self.request.get('diet_info')
		inputUserData(email, first_name, last_name, user_name, diet_info)
		self.redirect("/auth/holder_log")	

class About(Handler):
	def get(self):
		self.render('about.html')


application = webapp2.WSGIApplication([('/', PublicHome),
									   ('/auth/rsvp', Rsvp),
									   ('/auth/signup', SignUp),
									   ('/about', About)],
									    debug=True)
