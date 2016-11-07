from models import Post, Reply
from google.appengine.ext import ndb

def get_query_for_all_posts():
    """ Returns a query for all OBJECTS for this user. """
    return Post.query().order(Post.time)

def get_post_by_id(post_id):
    """ Returns a query for all OBJECTS for this user. """
    return Post.get_by_id(int(post_id))

def get_replies_for_post_by_id(post_id):
    """ Returns a query for all OBJECTS for this user. """
#     return Reply.query(ancestor = ndb.Key('Post', post_id))
    return Reply.query(Reply.parent == ndb.Key('Post', post_id))