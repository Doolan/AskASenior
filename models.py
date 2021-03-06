'''
Created on Oct 24, 2016

@author: nygrendr
'''

from google.appengine.ext import ndb
from google.appengine.api import blobstore
from google.appengine.api.blobstore.blobstore import BlobKey
from google.appengine.ext.webapp import blobstore_handlers


class User(ndb.Model):
    ID = ndb.StringProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    name = ndb.StringProperty()
    description = ndb.StringProperty(default="Hi, I'm boring and haven't filled out my profile description yet!")
    image_blob_key = ndb.BlobKeyProperty()
    #year = ndb.IntgerProperty()


class Post(ndb.Model):
    #category = ndb.StringProperty(repeated=True)
    type = ndb.StringProperty()
    category = ndb.StringProperty()
    author = ndb.KeyProperty(kind=User)
    is_anonymous = ndb.BooleanProperty()
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)


class Reply(ndb.Model):
    parent = ndb.KeyProperty(kind=Post)
    author = ndb.KeyProperty(kind=User)
#     up_votes = ndb.KeyProperty(kind=User, repeated=True, default=None)
#     down_votes = ndb.KeyProperty(kind=User, repeated=True, default=None)
    text = ndb.TextProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
