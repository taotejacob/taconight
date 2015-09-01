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


logout_url = users.create_logout_url('/log-out')
login_url = users.create_login_url('/log-in')

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
	invited = ndb.IntegerProperty()
	attendees = ndb.StringProperty()
	completed = ndb.IntegerProperty()
	messages = ndb.TextProperty()
	max_attend = ndb.IntegerProperty()
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
	approved = ndb.IntegerProperty()



#####################################
##
##  Webpage handlers
##
#####################################



class PublicHome(Handler):
	def get(self):
		self.render('publichome.html',
			logout_url = logout_url)

class Rsvp(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q < 1:
			self.redirect('/auth/signup')

		self.render('rsvp.html',
			logout_url = logout_url)



def inputUserData(first_name, last_name, user_name, diet_info):
	p = Account(username = user_name.nickname(),
				email = user_name.email(),
				first_name = first_name,
				last_name = last_name,
				first_last = first_name + " " + last_name[0],
				attendance = 0,
				diet_info = "Vegan:0, Vegitarian:0, Kosher:0",
				approved = 0
				)
	p.put()


class Tester(Handler):
	def get(self):
		self.render('tester.html')

class SignUp(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q > 0:
			self.redirect('/auth/rsvp')

		self.render('signup.html')

	def post(self):
		user_name = users.get_current_user()
		first_name = self.request.get('first_name')
		last_name = self.request.get('last_name')
		diet_info = self.request.get_all('diet_info')
		inputUserData(first_name, last_name, user_name, diet_info)
		self.redirect("welcome")	

class Welcome(Handler):
	def get(self):
		user_name = users.get_current_user()

		#Test if user is registered
		q = Account.query(Account.username == user_name.nickname()).count()
		if q < 1:
			self.redirect('/auth/signup')

		self.render('welcome.html')

class Logout(Handler):
	def get(self):
		self.redirect('/')

class About(Handler):
	def get(self):
		self.render('about.html')

class Admin(Handler):
	def get(self):
		self.render('admin.html')


application = webapp2.WSGIApplication([('/', PublicHome),
									   ('/auth/rsvp', Rsvp),
									   ('/auth/signup', SignUp),
									   ('/about', About),
									   ('/auth/welcome', Welcome),
									   ('/log-out', Logout),
									   ('/_admin/admin', Admin),
									   ('/tester', Tester)],
									    debug=True)
