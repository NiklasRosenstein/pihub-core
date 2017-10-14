
import flask
import {Middleware} from './base'


class PublishFlaskObject(Middleware):
  """
  Publishes an object in `flask.g` before a request is handled.
  """

  def __init__(self, name, obj):
    self.name = name
    self.obj = obj

  def before_request(self):
    setattr(flask.g, self.name, self.obj)
