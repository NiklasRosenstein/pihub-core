
import axios from 'axios'
import React from 'react'
import {Route} from 'react-router-dom'
const dashboard = require('@pihub/core/components/dashboard')

dashboard.menu.push({
  'url': '/scheduler',
  'text': 'Scheduler Overview',
  'icon': 'browser'
})

class SchedulerComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {jobs: []}
  }
  componentDidMount() {
    axios.get('/scheduler/jobs', {responseType: 'json'})
    .then(response => {
      this.setState({jobs: response.data.jobs})
    })
  }
  render() {
    return <dashboard.Dashboard title="Scheduler Overview">
      <table className="ui celled table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Name</th>
            <th>Trigger</th>
            <th>Executor</th>
            <th>Max Instances</th>
            <th>Next Run</th>
          </tr>
        </thead>
        <tbody>
          {this.state.jobs.map(job =>
            <tr key={job.id}>
              <td>{job.id}</td>
              <td>{job.name}</td>
              <td>{job.trigger}</td>
              <td>{job.executor}</td>
              <td>{job.max_instances}</td>
              <td>{job.next_run_time}</td>
            </tr>
          )}
        </tbody>
      </table>
    </dashboard.Dashboard>
  }
}

export const routes = [
  <Route path="/scheduler" component={SchedulerComponent}/>
]
