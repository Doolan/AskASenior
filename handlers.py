import json
import logging
import os

import jinja2
from rosefire import RosefireTokenVerifier
import webapp2
from webapp2_extras import sessions
from models import (User, Post, Reply)
from utils import user_utils

# This normally shouldn't be checked into Git
ROSEFIRE_SECRET = '5LgLSINSUKGVbkwTw0ue'

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)


class BaseHandler(webapp2.RequestHandler):
    def __init__(self, request=None, response=None):
        super().__init__(request=None, response=None)
        self.session_store = sessions.get_store(request=self.request)

    def dispatch(self):
        # Get a session store for this request.
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


class PostAction(BaseHandler):
    """Actions related to Posts"""

    def post(self):
        user = user_utils.get_user_from_rosefire_user(self.user())
        post = Post(category=self.request.get('category'), author=user.key,
                    is_anonymous=self.request.get('is_anonymous'), text=self.request.get('text'))
        post.put()
        self.redirect(self.request.referer)