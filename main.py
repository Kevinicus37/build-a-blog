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
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
def get_posts(limit, offset):
    blogs = db.GqlQuery('SELECT * FROM Blog '
                        'ORDER BY created DESC '
                        'LIMIT ' + str(limit) + ' OFFSET ' + str(offset))
    return blogs

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title=db.StringProperty(required=True)
    blog_post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.redirect('/blog')

class BlogPage(Handler):
    def render_front(self, page):
        offset=0
        page_size=5

        if page:
            page=int(page)
            offset=(page-1)*5
        else:
            page=1

        blogs = get_posts(page_size,offset)
        offset=(page*5)
        count = blogs.count(offset=offset, limit=page_size)

        self.render('blog.html', blogs=blogs, page=page, count=count)

    def get(self):
        page=self.request.get('page')
        self.render_front(page)


class NewPost(Handler):
    def render_front(self, title="", blog_post="", error=""):
        self.render('newpost.html', title=title, blog_post=blog_post, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog_post = self.request.get("blog_post")

        if title and blog_post:
            a = Blog(title = title, blog_post=blog_post)
            a.put()
            id=str(a.key().id())
            self.redirect("/blog/" + id)
        else:
            error = "we need both a title and a blog submission!"
            self.render_front(title=title, blog_post=blog_post, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        id=int(id)
        current_post = Blog.get_by_id(id)

        if current_post:
            self.render('post.html', current_post=current_post)

        else:
            error = "there is no post with id %s" % id
            self.render('404.html', error=error)


app = webapp2.WSGIApplication([
    ('/', MainPage), ('/blog', BlogPage), ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
