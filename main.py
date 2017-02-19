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
    "/newpost"
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
        base = db.GqlQuery("SELECT * FROM Entries "
                            "ORDER BY created DESC ")
        self.render("base.html", title = title, entryText = entryText, error = error)

    def get(self):
        self.render_base()

    def post(self):
        title = self.request.get("title")
        entryText = self.request.get("entryText")

        if title and entryText:
            e = Entries(title = title, entryText = entryText)
            e.put()
            self.redirect("/base")
        else:
            error = "We need both a title for the entry and some text IN the entry!"
            self.render_base(title, entryText, error)

class Blog(Handler):
    #def render_front(self, title="", entryText="", error=""):

    def render_login_form(self, error=""):
        t = jinja_env.get_template("blog.html")
        content = t.render(error=error)
        self.response.write(content)

    def get(self):
        """ Display a list of posts that have recently been created """

        # query for watched movies (by any user), sorted by how recently the movie was watched
        query = NewPost.all().order("-datetime")
        blog = db.GqlQuery("SELECT * FROM  NewPost"
                            "ORDER BY created DESC ")
        NewPost = query.fetch(limit = 5)

        self.render("blog.html", title = title, entryText = entryText, error = error)


app = webapp2.WSGIApplication([('/', MainPage), ('/blog', Blog)
], debug=True)
