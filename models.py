'''
Created on Oct 24, 2016

@author: nygrendr
'''

from google.appengine.ext import ndb


class User(ndb.Model):
    ID = ndb.StringProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    #year = ndb.IntgerProperty()


class Post(ndb.Model):
    #category = ndb.StringProperty(repeated=True)
    category = ndb.StringProperty()
    author = ndb.KeyProperty(kind=User)
    is_anonymous = ndb.BooleanProperty()
    text = ndb.TextProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)


class Reply(ndb.Model):
    parent = ndb.KeyProperty(kind=Post)
    author = ndb.KeyProperty(kind=User)
    up_votes = ndb.KeyProperty(kind=User, repeated=True)
    down_votes = ndb.KeyProperty(kind=User, repeated=True)
    text = ndb.TextProperty()
    time = ndb.DateTimeProperty()
