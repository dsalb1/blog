import jinja2
import webapp2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def get(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.response.write(self.render_str(template, **kw))

class BlogPost(db.Model):
	title = db.StringProperty(required = True)
	blogpost = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)


def get_posts(limit, offset):
	posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT {0} OFFSET {1}".format(limit, offset))
	return posts

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.redirect('/blog')

class MainBlog(Handler):
	def get(self):
		page_num = self.request.get("page", 0)
		page_num = page_num and int(page_num)

		page_size = 5
		offset = 5 * page_num
		posts = get_posts(page_size, offset)
		post_count = posts.count(offset=offset, limit=page_size)
		#self.response.write(post_count)
		self.render('blog.html', posts=posts, page_num = page_num, post_count = post_count)


	"""def post(self):
		title = self.request.get("title")
		blogpost = self.request.get("blogpost")

		if title and blogpost:
			self.redirect()
		else:
			error="You need to fill out both fields to post a new entry"
			self.render("base.html", error=error)"""

class NewPost(Handler):
	def get(self):
		self.render("newpost.html")

	def post(self):
		title = self.request.get("title")
		blogpost = self.request.get("blogpost")

		if title and blogpost:
			p = BlogPost(title=title, blogpost=blogpost)
			p.put()

			self.redirect('/blog/' + str(p.key().id()))
		else:
			error="You need to fill out both fields to post a new entry"
			self.render("newpost.html", title=title, blogpost=blogpost, error=error)

class ViewPostHandler(Handler):
	def get(self, id):
		if BlogPost.get_by_id(int(id)):
			new_post = BlogPost.get_by_id(int(id))
			self.render("post.html", post=new_post)



app = webapp2.WSGIApplication([
	('/', MainPage),
	('/blog', MainBlog),
	('/blog/newpost', NewPost),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
