
import flask
import {Middleware} from './base'


class PublishRequestObject(Middleware):
  """
  Publishes an object in `flask.request` before a request is handled.
  """

  def __init__(self, name, obj):
    self.name = name
    self.obj = obj

  def before_request(self):
    setattr(flask.request, self.name, self.obj)
