import React from 'react'
import ReactDOM from 'react-dom'
import {BrowserRouter, IndexRoute, Route} from 'react-router-dom'

// TODO: How to make jQuery available to semantic.min.js?
// import 'semantic-ui-css/semantic.min.js'
import 'semantic-ui-css/semantic.min.css'

{{# This will be preprocessed using a Ninja-template to insert all #}}
{{# the routes registered to the main application. #}}
function initWebModules(routes) {
  let curr_module = null
  let other_module = null
  {{# Load all routes into the routes array and wire modules together. #}}
  {{% for module_name in pihub.web_modules %}}
  curr_module = require('{{@ module_name @}}')
  Array.prototype.push.apply(routes, curr_module.routes)
  {{% endfor %}}
}

let routes = []
initWebModules(routes)

let router = <BrowserRouter>
  {React.createElement('div', {style: {height: '100%'}}, ...routes)}
</BrowserRouter>

ReactDOM.render(router, document.getElementById('container'))
