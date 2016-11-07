import json
import os

import jinja2
import webapp2
from handlers import BaseHandler
from rosefire import RosefireTokenVerifier

from models import Reply
from postHandlers import PostListHandler, ViewPostHandler, PostAction
from utils import post_utils, user_utils

# This normally shouldn't be checked into Git
ROSEFIRE_SECRET = '5LgLSINSUKGVbkwTw0ue'

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)


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
