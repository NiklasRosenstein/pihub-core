"""
Monkey-patch for the Werkzeug application reloader.
"""

import nodepy
import functools
import sys
import werkzeug._reloader as _reloader

_installed = False


def monkey_patch(obj, member):
  """
  Monkey-patch a function called *member* in *obj* with the decorated function.
  The original member value will be passed as the first argument.
  """

  _old = getattr(obj, member)
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
      return func(_old, *args, **kwargs)
    setattr(obj, member, wrapper)
    return wrapper
  return decorator


def install():
  """
  Installs the patch for the `werkzeug._reloader` module.
  """

  global _installed
  if _installed: return

  if _reloader.reloader_loops['auto'] == _reloader.reloader_loops['watchdog']:
    print("[werkzeug-patch - WARNING]: default reloader is 'watchdog', "
          "werkzeug-patch only supports 'stat'.", file=sys.stderr)

  @monkey_patch(_reloader, '_iter_module_files')
  def _iter_module_files(__old):
    yield from __old()
    for module in require.context.modules.values():
      yield str(module.filename)

  @monkey_patch(_reloader, '_get_args_for_reloading')
  def _get_args_for_reloading(__old):
    args = __old()
    if not nodepy.runtime.script:
      args[0:1] = nodepy.runtime.exec_args
    return args

  _installed = True
