from models import Post

def get_query_for_all_posts():
    """ Returns a query for all OBJECTS for this user. """
    return Post.query().order(Post.time)