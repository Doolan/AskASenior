from google.appengine.ext import ndb

from models import User
import logging


def get_user_from_rosefire_user(rf_user):
    user = User.get_by_id(rf_user.email, parent=get_parent_key_from_email(rf_user.email))
    if not user:
        logging.info("Failed to find player by id, creating new user")
        user = User(parent=get_parent_key_from_email(rf_user.email), id=rf_user.email,
                    username=rf_user.username, email=rf_user.email)
        user.put()
    return user


def get_parent_key_from_email(email):
    return ndb.Key("Entity", email.lower())