import json
import os

import jinja2

from handlers import BaseHandler
from models import Post
from utils import post_utils, user_utils

# This normally shouldn't be checked into Git
ROSEFIRE_SECRET = '5LgLSINSUKGVbkwTw0ue'

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)


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

        # self.response.headers['Content-Type'] = 'text/plain'
        #         self.response.write(self.request.GET['resp'])
        post_id = self.request.get("post_id")

        post_query = post_utils.get_post_by_id(int(post_id))
        reply_query = post_utils.get_replies_for_post_by_id(int(post_id))
        template = JINJA_ENV.get_template("templates/view-post.html")
        values = {"post": post_query,
                  "post_id": post_id,
                  "reply_query": reply_query}
        self.response.out.write(template.render(values))


class PostAction(BaseHandler):
    """Actions related to Posts"""

    def post(self):
        is_anonymous = self.request.get('is_anonymous') == 'true'
            
        user = user_utils.get_user_from_rosefire_user(self.user())
        post = Post(title=self.request.get('title'), type=self.request.get('type'), category=self.request.get('category'), author=user.key,
                    is_anonymous=is_anonymous, body=self.request.get('body'))
        post.put()
        self.redirect(self.request.referer)
