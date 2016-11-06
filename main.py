import json
import logging
import os

import jinja2
from rosefire import RosefireTokenVerifier
import webapp2
from webapp2_extras import sessions
import handlers
from models import Post, Reply
import user_utils
import post_utils

# This normally shouldn't be checked into Git
ROSEFIRE_SECRET = '5LgLSINSUKGVbkwTw0ue'

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)


# From: https://webapp2.readthedocs.io/en/latest/api/webapp2_extras/sessions.html
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def user(self):
        if "user_info" not in self.session:
            token = self.request.get('token')
            auth_data = RosefireTokenVerifier(ROSEFIRE_SECRET).verify(token)
            user_info = {"name": auth_data.name,
                         "username": auth_data.username,
                         "email": auth_data.email,
                         "role": auth_data.group}
            self.session["user_info"] = json.dumps(user_info)
        return self.session.get("user_info")


class MainHandler(BaseHandler):
    def get(self):
        template = JINJA_ENV.get_template("templates/index.html")
        if "user_info" in self.session:
            #             user_info = json.loads(self.session["user_info"])
            #             print("user_info", user_info)
            #             self.response.out.write(template.render({"user_info": user_info}))
            self.redirect("/post-list")
            return
        else:
            self.response.out.write(template.render())


class PostListHandler(BaseHandler):
    def update_values(self, values):
        values["post_query"] = post_utils.get_query_for_all_posts()

    def get_page_title(self):
        return "Posts"

    def get_template(self):
        return "templates/post-list.html"

    def get(self):
        if "user_info" not in self.session:
            #            raise Exception("Missing user!")
            self.redirect("/")
            return

        else:
            user_info = json.loads(self.session.get("user_info"))
            email = user_info["email"]

        query = post_utils.get_query_for_all_posts()
        template = JINJA_ENV.get_template("templates/post-list.html")
        values = {"post_query": query}
        self.response.out.write(template.render(values))


class ViewPostHandler(BaseHandler):
    def get_page_title(self):
        return "View Post"

    def get(self):
        if "user_info" not in self.session:
            #            raise Exception("Missing user!")
            self.redirect("/")
            return

        else:
            user_info = json.loads(self.session.get("user_info"))
            email = user_info["email"]

        #         self.response.headers['Content-Type'] = 'text/plain'
        #         self.response.write(self.request.GET['resp'])
        post_id = self.request.get("post_id")

        post_query = post_utils.get_post_by_id(int(post_id))
        reply_query = post_utils.get_replies_for_post_by_id(int(post_id))
        template = JINJA_ENV.get_template("templates/view-post.html")
        values = {"post": post_query,
                  "post_id": post_id,
                  "reply_query": reply_query}
        self.response.out.write(template.render(values))


# Auth handlers
class LoginHandler(BaseHandler):
    def get(self):
        if "user_info" not in self.session:
            token = self.request.get('token')
            auth_data = RosefireTokenVerifier(ROSEFIRE_SECRET).verify(token)
            user_info = {"name": auth_data.name,
                         "username": auth_data.username,
                         "email": auth_data.email,
                         "role": auth_data.group}
            self.session["user_info"] = json.dumps(user_info)
        self.redirect(uri="/")


class LogoutHandler(BaseHandler):
    def get(self):
        del self.session["user_info"]
        self.redirect(uri="/")


class PostAction(BaseHandler):
    """Actions related to Posts"""

    def post(self):
        user = user_utils.get_user_from_rosefire_user(self.user())
        post = Post(category=self.request.get('category'), author=user.key,
                    is_anonymous=False, text=self.request.get('text'))
        post.put()
        self.redirect(self.request.referer)


class InsertReplyAction(BaseHandler):
    """Actions related to Posts"""

    def post(self):
        user = user_utils.get_user_from_rosefire_user(self.user())
        post = post_utils.get_post_by_id(int(self.request.get('post_id')))
        reply = Reply(parent=post.key, author=user.key, text=self.request.get('text'))
        reply.put()
        self.redirect(self.request.referer)


config = {}
config['webapp2_extras.sessions'] = {
    # This key is used to encrypt your sessions
    'secret_key': 'SECRETSAUCE2',
}

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    # Auth
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    # Pages
    ('/post-list', PostListHandler),
    ('/view-post', ViewPostHandler),

    # Actions
    ('/post', PostAction),
    ('/insert-reply', InsertReplyAction)
], config=config, debug=True)
