<img src="static/pihub-core/logo.png" align="right">

# PiHub

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
which can be loaded using `@pihub/core/components/base:load_component(name)`.
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
