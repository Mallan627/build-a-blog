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
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

allowed_routes = [
    "/base",
    "/blog",
    "/newpost",
    "/allentries"
#    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
]

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    #take template name and returns a string of rendered template
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entries(db.Model):
    title = db.StringProperty(required = True)
    entryText = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#class NewPost(db.Model):
#    title = db.StringProperty(required = True)
    # entryText = db.TextProperty(required = True)
    # created = db.DateTimeProperty(auto_now_add = True)
    #
    # t = jinja_env.get_template("newpost.html")
    # content = t.render(title = title, entryText = entryText)
    # self.response.write(content)

class MainPage(Handler):
    def render_base(self, title="", entryText="", error=""):
        base = db.GqlQuery("SELECT * FROM Entries ORDER BY created DESC ")
        self.render("base.html", base = base)

    def get(self):
        self.render_base()

    def post(self):
        title = self.request.get("title")
        entryText = self.request.get("entryText")

        if title and entryText:
            e = Entries(title = title, entryText = entryText)
            e.put()
            self.redirect("/")
        else:
            error = "We need both a title for the entry and some text IN the entry!"
            self.render_base(title, entryText, error)

class Blog(Handler):
    #def render_front(self, title="", entryText="", error=""):

    def render_blog(self, title="", entryText = "", error=""):
        blog = db.GqlQuery("SELECT * FROM Entries ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blog = blog)

    def get(self):
        """ Display a list of posts that have recently been created """
        self.render_blog()

class Allentries(Handler):
    def render_blog(self, title="", entryText = "", error=""):
        base = db.GqlQuery("SELECT * FROM Entries ORDER BY created DESC ")
        self.render("allentries.html", base = base)

    def get(self):
        """ Display a list ALL posts in desc order of creation """
        self.render_blog()

class Newpost(Handler):
    def render_newpost(self, title="", entryText = "", error = ""):
        t = jinja_env.get_template("newpost.html")
        self.response.write(t.render(title=title, entryText=entryText, error=error))

    def post(self):
        title = self.request.get("title")
        entryText = self.request.get("entryText")
        if title and entryText:
            e = Entries(title = title, entryText = entryText)
            e.put()
            self.redirect("/blog")
        else:
            error = "We need both a title for the entry and some text IN the entry!"
            self.render_newpost(title, entryText, error)

    def get(self):
        title = self.request.get("title")
        entryText = self.request.get("entryText")
        self.render_newpost("", "", "")

#class ViewPostHandler(webapp2.RequestHandler):
#    def get(self, id):

app = webapp2.WSGIApplication([('/', MainPage), ('/blog', Blog), ('/allentries', Allentries), ('/newpost', Newpost)
], debug=True)
