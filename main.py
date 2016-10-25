import json
import logging
import os

import jinja2
from rosefire import RosefireTokenVerifier
import webapp2
from webapp2_extras import sessions
import handlers
from models import Post
import user_utils

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
        return self.session


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
#     def update_values(self, email, values):
#         values["password_query"] = utils.get_query_for_all_passwords_for_email(email)
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
            user_info=json.loads(self.session.get("user_info"))
            email = user_info["email"]

#         query = utils.get_query_for_all_passwords_for_email(email)
        template = JINJA_ENV.get_template("templates/post-list.html")
#         values = {"user_email": email,
#                   "logout_url": users.create_logout_url("/"),
#                   "password_query": query,
#                   "login_method": login_method}
        self.response.out.write(template.render())


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
                    is_anonymous=self.request.get('is_anonymous'), text=self.request.get('text'))
        post.put()
        self.redirect(self.request.referer)

config = {}
config['webapp2_extras.sessions'] = {
    # This key is used to encrypt your sessions
    'secret_key': 'SECRETSAUCE2',
}

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/post-list', PostListHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/post', PostAction)
], config=config, debug=True)
