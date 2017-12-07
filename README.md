<img src="www/logo.png" align="right">

## @pihub/core

*This is the PiHub core application package.*

PiHub is a Python web application with a React frontend. It's main goal is to
provide an easily extensible web application infrastructure for composing
pre-built components, ultimately allowing users to create their own deployments
à la Home Assistant on, for example, a RaspberryPi. It's secondary goal is to
allow using PiHub as a basis for Python+React based application.

__To do__

* Database migration API (ideally, using the upcoming Pony Migration tool)


### Installation

#### Requirements

* [Python 3.3+](https://python.org)
* [Node.py 2.1+](https://nodepy.org)
* [Yarn](https://yarnpkg.com/lang/en/)

#### Installing @pihub/core

    $ export PATH=".nodepy/bin:$PATH"
    $ nodepy-pm install git+https://github.com/pihub-framework/pihub-core.git
    $ pihub --version
    1.0.0-dev

#### Configuration

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


### Deployment

The `pihub` CLI orchestrates the deployment process (and is also useful during
development). After you've set up your PiHub configuration, you must install
the JavaScript dependencies required by your PiHub components and build a
web bundle. After that, you can start the development server.

    $ pihub bundle install
    $ pihub bundle build
    $ pihub bundle wsgi --debug

To deploy PiHub on a production server, use the `@pihub/core/app:init()`
function to initialize the PiHub application, perform a database consistency
check and retrieve the Flask application object.

    $ ls -a
    .nodepy  build  main.py  Procfile  pihub.config.py
    $ cat Procfile
    web: gunicorn main:application
    $ cat main.py
    import nodepy
    application = nodepy.require('@pihub/core/app').init()


### Concepts

#### Components

PiHub components a are two-fold: They always consist of a Node.py Python
module and a JavaScript module. One Node.py package can expose multiple
PiHub components.

The Python module of the PiHub component must define a `__component_meta__`
member. If the component wishes to declare database entities, it needs to
specify the `'database_revision'` key in the metadata.

```python
# mypihubextension/components/somecomp.py
__component_meta__ = {
  'database_revision': 1
}

import {app, config, database} from '@pihub/core'

# ... Do whatever you want, eg. define new routes in the Flask app
```

The **JavaScript** module must reside in the `www/` subdirectory of the
component and must have the same name and and path relative to the `www/`
directory as the Python module to the package's `resolve_root`. Thus, if
you don't define a `resolve_root` in the Node.py package manifest, and you
component is in `components/somecomp.py`, then the JavaScript module must be
at `www/components/somecomp.py`.

The JavaScript module *must* export a `routes` member that is a list of
React routes. Example:

```js
// mypihubextension/www/components/somecomp.jsx
import React from 'react'
const dashboard = require('@pihub/core/components/dashboard')  // TODO: How to get the same object with `import ... from ...`?

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


#### Component Metadata

The `__component_meta__` member is mandatory in the Python module for every
PiHub component. The following entries are currently taken into account:

##### `requires`

A list of other component names that your component depends on.

##### `database_revision`

The revision number of the component's database schema. If the revision number
for a component changes during the lifecycle of a production instance, a
migration will be triggered by calling the `execute_migration(from_, to)`
function in your Python module.

*This metadata key is only required when using the `@pihub/core/database`
component.*
