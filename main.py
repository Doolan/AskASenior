import json
import os

import jinja2
import time
import webapp2
from google.appengine.ext import ndb
from webapp2_extras import sessions
import handlers
from models import Post, Reply, User
from handlers import BaseHandler
from rosefire import RosefireTokenVerifier

from google.appengine.api import blobstore
from google.appengine.api.blobstore.blobstore import BlobKey
from google.appengine.ext.webapp import blobstore_handlers
import logging

from models import Reply
from postHandlers import PostListHandler, ViewPostHandler, PostAction
from utils import post_utils, user_utils

# This normally shouldn't be checked into Git
ROSEFIRE_SECRET = '5LgLSINSUKGVbkwTw0ue'
UNIVERSAL_PARENT = ndb.Key("Entity",'DARTH_VADER')


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


class ViewProfileHandler(BaseHandler):
    # def get_page_title(self):
    #     return "View Post"

    def get(self):
        is_self = False

        if "user_info" not in self.session:
            #            raise Exception("Missing user!")
            self.redirect("/")
            return

        else:
            user_utils.get_user_from_rosefire_user(self.user())
            username = self.request.get('username', 'none')
            if username == 'none':
                user_info = json.loads(self.session.get("user_info"))
                user = user_utils.get_user_from_username(user_info["username"])
                is_self = True
                print("user info", user_info)
            else:
                userResults = User.query(User.username == username).fetch(limit=1)
                if len(userResults) == 0:
                    self.redirect(uri="/profile")
                    return
                else:
                    user = userResults[0]

            print("user", user)

            query = post_utils.get_query_for_all_nonanonymous_posts_by_user(user)
            values = {"post_query": query,
                      "user": user,
                      "is_self": is_self}

            values["form_action"] = blobstore.create_upload_url('/update-profile')

            template = JINJA_ENV.get_template("templates/profile.html")

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


class InsertReplyAction(BaseHandler):
    """Actions related to Posts"""

    def post(self):
        user = user_utils.get_user_from_rosefire_user(self.user())
        post = post_utils.get_post_by_id(int(self.request.get('post_id')))
        reply = Reply(parent=post.key, author=user.key, text=self.request.get('text'))
        reply.put()
        time.sleep(.5)
        self.redirect(self.request.referer)


class UpdateProfileAction(handlers.BaseBlobstoreHandler):
    def post(self):
        logging.info("Received an image blob with this data.")
        userdata = user_utils.get_user_from_rosefire_user(self.user())
        if len(self.get_uploads()) > 0:
            media_blob = self.get_uploads()[0]
            userdata.image_blob_key = media_blob.key()
        userdata.description = self.request.get('profile-description')
        userdata.put()
        #time.sleep(.5)
        self.redirect("/profile")


# self.response.on_completion()



config = {}
config['webapp2_extras.sessions'] = {
    # This key is used to encrypt your sessions
    'secret_key': 'SECRETSAUCE2',
}

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/img/([^/]+)?', handlers.BlobServer),
    # Auth
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    # Pages
    ('/post-list', PostListHandler),
    ('/view-post', ViewPostHandler),
    ('/profile', ViewProfileHandler),
    # Actions
    ('/post', PostAction),
    ('/insert-reply', InsertReplyAction),
    ('/update-profile', UpdateProfileAction)
], config=config, debug=True)
