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
import webapp2
import cgi
import jinja2
import os
import re
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))



class BlogEntries(db.Model):
    subject = db.TextProperty(required = False)
    content = db.TextProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainHandler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
    The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

# class ViewPostHandler(webapp2.RequestHandler):
#     """ creates unique IDs """
#     def get(self,id):
#         id_RE = re.compile(id)
#         self.response.write(id_RE)


class Index(MainHandler):
    """ Handles requests coming in to '/' (the root of our site)
    """

    def get(self):
        # pull 5 most recent posts
        last5 = db.GqlQuery("SELECT * FROM BlogEntries ORDER BY created DESC LIMIT 5 ")
        #last5 = (['ayo', 'yayo'], ['post1', 'post1'], ['post2', 'post2'], ['post3', 'post3'], ['post4', 'post4'])

        t = jinja_env.get_template("frontpage.html")
        content = t.render(five_recent = last5)
        self.response.write(content)

class NewPost(MainHandler):
    """ write new post
    """
    def get(self):
        #unwatched_movies = db.GqlQuery("SELECT * FROM Movie where watched = False")
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

class ViewPost(MainHandler):
    """ view post
    """
    def post(self):
        new_post_content = self.request.get("new-post-content")
        new_post_content_esc = cgi.escape(new_post_content, quote=True)

        new_post_subject = self.request.get("subject")
        new_post_subject_esc = cgi.escape(new_post_subject, quote=True)

        # construct a blog object for the new entry
        blogentry = BlogEntries(subject = new_post_subject_esc, content = new_post_content_esc)
        #blogentry = BlogEntries(subject = new_post_subject_esc)
        blogentry.put()

        t = jinja_env.get_template("blogview.html")
        content = t.render(blogentry = blogentry)
        self.response.write(content)


# webapp2 route
# app = webapp2.Route('/<id:\d+>', ViewPostHandler)

app = webapp2.WSGIApplication([
    ('/', Index),
    ('/newpost', NewPost),
    ('/view', ViewPost)
], debug=True)
