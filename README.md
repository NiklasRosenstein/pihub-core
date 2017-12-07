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


### Concepts

PiHub uses Node.py for its import-mechanism and its package management, as
it fits the bill better than using Pip and standard Python modules. Installing
new components is a pain-less process of using the `nodepy-pm` CLI and
updating the PiHub configuration.

Components in PiHub are two-fold: For once they are a Node.py Python module
that is requirable from the `@pihub/core/component` module, but usually they
also come with a **Web Module**. All web modules must lie inside the `www`
directory of their respective Node.py package directory. They will be joined
into a single codebase by the `pihub bundle` command to produce a bundle with
Webpack.

Step to create a new PiHub component:

1. Create a `nodepy.json` file in your component's package directory and call
    your package `@pihub-contrib/my-component`
2. (Optional) Create a `package.json` file if your component requires 
    additional JavaScript dependencies
3. Create a `index.py` file that contains your components' Python code
4. Create a `www/@pihub-contrib/my-component.jsx` file that contains your
    components' React code

**nodepy.json**:

```json
{
    "name": "@pihub-contrib/my-component",
    "version": "1.0.0"
}
```

**index.py**:

```python
import {app, config} from '@pihub/core'

# This will load the www/@pihub-contrib/my-component module in the
# PiHub web entry point.
config.add_web_module('@pihub-contrib/my-component')

# Do whatever you want here, eg. registering new routes to the Flask `app`
```

**www/@pihub-contrib/my-component.jsx**:

```js
import React from 'react'
const dashboard = require('@pihub/core/components/dashboard')

const URL = '/my-component'

dashboard.menu.push({
  'url': URL,
  'text': 'My Component!'
})

class MyComponent extends React.Component {
  render() {
    return <div>Hello from MyComponent!</div>
  }
}

// These routes will be added to the react BrowserRouter.
exports const routes = [
  <Route exact path={URL} component={MyComponent}/>
]
```
