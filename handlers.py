import json
import os

import jinja2
import webapp2
from rosefire import RosefireTokenVerifier
from webapp2_extras import sessions

from models import (Post)

# This normally shouldn't be checked into Git
from user_utils import get_user_from_rosefire_user

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
        user = get_user_from_rosefire_user(self.user())
        post = Post(category=self.request.get('category'), author=user.key,
                    is_anonymous=self.request.get('is_anonymous'), text=self.request.get('text'))
        post.put()
        self.redirect(self.request.referer)