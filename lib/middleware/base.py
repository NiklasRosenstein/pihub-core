"""
Interface for Flask middlewares.
"""

class Middleware:

  def before_first_request(self):
    pass

  def before_request(self):
    pass

  def after_request(self, response):
    return response
