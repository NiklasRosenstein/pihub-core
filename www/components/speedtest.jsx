
import axios from 'axios'
import React from 'react'
import Plot from 'react-plotly.js'
import {Route} from 'react-router-dom'
import {menu, Dashboard} from '@pihub/core/components/dashboard'

const RawHTML = ({children, className = ""}) =>
  <div className={className} dangerouslySetInnerHTML={{__html: children}}></div>

class Speedtest extends React.Component {
  constructor(props) {
    super(props)
    this.state = {dates: [], down: [], up: [], ping: []}
  }
  componentDidMount() {
    axios.get('/speedtest/data', {responseType: 'json'})
    .then(response => {
      let data = response.data.speedtests;
      this.setState(state => {
        state.dates = data.map(x => x.start)
        state.down = data.map(x => x.down)
        state.up = data.map(x => x.up)
        state.ping = data.map(x => x.ping)
        console.log(state.dates)
        console.log(state.down)
        console.log(state.up)
        console.log(state.ping)
        return state
      })
    })
  }
  render() {
    return <Dashboard title="Speedtest">
      <Plot data={[
        {
          type: 'scatter',
          mode: 'lines+points',
          x: this.state.dates,
          y: this.state.down
        },
        {
          type: 'scatter',
          x: this.state.dates,
          y: this.state.up
        },
        {
          type: 'scatter',
          x: this.state.dates,
          y: this.state.ping,
          xaxis: 'x2',
          yaxis: 'y2'
        }
      ]}
      layout={{
        // TODO: How to make graph scale horizontally?
        autosize: true,
        xaxis: {domain: [0, 0.45]},
        yaxis2: {anchor: 'x2'},
        xaxis2: {domain: [0.55, 1]}
      }}/>
    </Dashboard>
  }
}

menu.push({
  'url': '/speedtest',
  'text': 'Speedtest',
  'icon': 'rocket'
})

export default {
  routes: [<Route path="/speedtest" component={Speedtest}/>],
  Speedtest
}
