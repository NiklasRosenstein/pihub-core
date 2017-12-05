import React from 'react'
import ReactDOM from 'react-dom'
import {BrowserRouter, IndexRoute, Route} from 'react-router-dom'

// This will be preprocessed using a Ninja-template to insert all
// the routes registered to the main application.
let routes = []
{{% for module in pihub.react_router_modules %}}
routes.push(require('{{@ module @}}'))
{{% endfor %}}

ReactDOM.render(
  <BrowserRouter>
    <div>
      {routes}
    </div>
  </BrowserRouter>,
  document.getElementById('container')
)
