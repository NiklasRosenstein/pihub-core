<img src="static/pihub-core/logo.png" align="right">

## @pihub/core

*This is the PiHub core application package.*

PiHub is a Python web application with a React frontend. It's main goal is to
provide an easily extensible web application infrastructure for composing
pre-built components, ultimately allowing users to create their own deployments
à la Home Assistant. It's secondary goal is to allow using PiHub as a basis
for Python+React based application.

### Installation

__Requirements__

* [Python 3.3+](https://python.org)
* [Node.py 2.1+](https://nodepy.org)
* [Yarn](https://yarnpkg.com/lang/en/)

__Installing @pihub/core__

    $ export PATH=".nodepy/bin:$PATH"
    $ nodepy-pm install git+https://github.com/pihub-framework/pihub-core.git
    $ pihub --version
    1.0.0-dev

__Configuration__

    $ cat pihub.config.py
    components = [
      '@pihub/core/components/auth',
      '@pihub/core/components/dashboard'
    ]
    auth = {
      'password': 'alpine'
    }
    database = {
      # PiHub uses Pony ORM. This will be passed to Database.bind().
      'provider': 'sqlite',
      'filename': str(module.directory.joinpath('pihub.sqlite'))
    }

__Deployment__

THe `pihub` CLI orchestrates the deployment process (and is also useful during
development). After you've set up your PiHub configuration, you must install
the JavaScript dependencies required by your PiHub components and build a
web bundle. After that, you can start the development server.

    $ pihub bundle install
    $ pihub bundle build
    $ pihub bundle wsgi --debug

To deploy PiHub on a production server, use the `@pihub/core/scripts/wsgi`
module and it's `application` member. For example:

    $ ls -a
    .nodepy  build  main.py  Procfile  pihub.config.py
    $ cat Procfile
    web: gunicorn main:application
    $ cat main.py
    import nodepy
    application = nodepy.require('@pihub/core/scripts/wsgi').application
