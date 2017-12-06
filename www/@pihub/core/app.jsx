import React from 'react'
import ReactDOM from 'react-dom'
import {BrowserRouter, IndexRoute, Route} from 'react-router-dom'

// TODO: How to make jQuery available to semantic.min.js?
// import 'semantic-ui-css/semantic.min.js'
import 'semantic-ui-css/semantic.min.css'

// This will be preprocessed using a Ninja-template to insert all
// the routes registered to the main application.
let routes = []
{{% for module in pihub.react_routes %}}
routes.push(require('{{@ module @}}').default)
{{% endfor %}}

let router = <BrowserRouter>
  {React.createElement('div', {style: {height: '100%'}}, ...routes)}
</BrowserRouter>

ReactDOM.render(router, document.getElementById('container'))
