<img src="static/pihub-core/logo.png" align="right">

## @pihub/core

*This is the PiHub core application package.*

PiHub is a framework for creating user personalized web applications by
combining prebuilt components. PiHub is built using

* [Python 3.3+](https://python.org)
* [Node.py](https://nodepy.org)
* [Flask](http://flask.pocoo.org/)
* [React.JS](https://reactjs.org/)
* [Webpack](https://webpack.js.org/)

### Configuration

First you need to install `@pihub/core`:

    $ nodepy-pm install git+https://github.com/pihub-framework/pihub-core.git

You configure PiHub using a `pihub.config.py` file in a directory of your
choice. That directory will be used to compile all JavaScript components
and this is where your PiHub application will be served from.

    $ cat pihub.config.py
    components = [
      '@pihub/core/components/auth',
      '@pihub/core/components/dashboard'
    ]
    auth = {
      'password': 'alpine'
    }

Now you only need to build the JavaScript bundle and run the server.

    $ nodepy-pm @pihub/core/scripts/bundle
    $ nodepy-pm @pihub/core/scripts/wsgi
