<img src="static/pihub-core/logo.png" align="right">

## @pihub/core

*This is the PiHub core application package.*

PiHub is a framework for creating user personalized web applications by
combining prebuilt componenets. PiHub is built using

* [Python 3.3+](https://python.org)
* [Node.py](https://nodepy.org)
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
      '@pihub/core:auth',
      '@pihub/core:dashboard'
    ]
    auth = {
      'password': 'welcome'
    }

To build the JavaScript bundle from the components that you want to use in
your PiHub deployment, run the bundler script:

    $ nodepy-pm @pihub/core/scripts/bundle --install
    Loaded 1 package(s) from 2 componenent(s).
    Found 2 React routes.
    Merging JavaScript codebase.
    Building bundle.
    Writing combined package.json
    Installing combined dependencies.
    $ yarn install --silent --no-lockfile
    $ yarn run webpack

And you're good to go:

    $ nodepy-pm @pihub/core/scripts/server


---

OLD README -- to be removed or updated

Component based framework for creating customizable applications. Delivers a
convenient API through the [Node.py Runtime][Node.py] and it's package
ecosystem.

  [Node.py]: https://nodepy.org/

## Getting Started

* Install Node.py 0.1.0 or newer on Python 3.5 or newer
* Install `@pihub/core` (eg. `nodepy-pm install -g git+https://github.com/pihub-framework/pihub-core.git`)

## Creating a new Component

Components are subclasses of the `@pihub/core/component:Component` class and
must be exposed in a Node.py package. The component is easily published by
adding a `[pihub.components]` section to the package manifest.

A component may depend on other components implicitly. It can find this
component in an initialized state using the `app.get_component(name)`
method. Many components will depend on the `@pihub/core:dashboard` component
to add their information.

> **Important**: Implicitly depending on a component does NOT automatically
> add the component to the PiHub application. It must still be configured
> to be loaded when PiHub starts.

```python
import {Component} from '@pihub/core/component'

class MyComponent(Component):

  def init_component(self, app):
    dashboard = app.get_component('@pihub/core:dashboard')
    # ...

module.exports = MyComponent
```

To publish the component:

```toml
[package]
name = "my-pihub-extension"
...

[pihub.components]
mycomponent = "./mycomponent"
```

The full name of this component is then `my-pihub-extensions:mycomponent`
which can be loaded using `@pihub/core/component:load_component(name)`.
Components specified in the PiHub configuration (`~/.pihub/config.py`) are
automatically loaded when PiHub starts. The order in the components list is
irrelevant.

```python
components = [
  '@pihub/core:dashboard',
  'my-pihub-extension:mycomponent'
]
```

## Replacing Components

Components can be replaced by injecting an alternative class into the
configuration's `component_hooks` dictionary. The `load_component()`
function will check this dictionary first before resolving the component
name further.

> **Important**: When the replaced component is required by other components,
> it must replicate the public interface of the original component!

```python
component_hooks = {
  '@pihub/core:dashboard': require('my-dashboard').MyDashboardClass
}
```
