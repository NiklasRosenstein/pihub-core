import axios from 'axios'
import styled from 'styled-components'
import React from 'react'
import {Link, Route, withRouter} from 'react-router-dom'

import logo from '@pihub/core/logo.png'

require('@pihub/core/components/dashboard').initCallbacks.push((dashboard) => {
  dashboard.state.menuLeft.push({
    'url': '/auth/signout',
    'text': 'Sign Out'
  })
})

const Wrapper = styled.div`
  background-color: #DADADA;
  height: 100%;
`

const Image = styled.img`
  display: inline !important;  // Overwritten by semantic-ui otherwise
  margin-top: -100px;
`

const Column = styled.div`
  max-width: 450px;
`

class AuthSignin extends React.Component {
  constructor(props) {
    super(props)
    this.state = {error: null, password: ''}
    this.handleChange = this.handleChange.bind(this)
    this.handleSubmit = this.handleSubmit.bind(this)
  }
  render() {
    return <Wrapper className="ui middle aligned center aligned grid">
      <Column className="column">
        <h2 className="ui teal image header">
          <Image src={logo}/>
          <div className="content">
            PiHub Authentication
          </div>
        </h2>
        <form className="ui large form" method="post" action="" onSubmit={this.handleSubmit}>
          <div className="ui stacked segment">
            <div className="field">
              <div className="ui left icon input">
                <i className="lock icon"></i>
                <input type="password" name="password" placeholder="Password" value={this.state.password} onChange={this.handleChange} autoFocus/>
              </div>
            </div>
            <div className="ui fluid large teal submit button" onClick={this.handleSubmit}>Submit</div>
          </div>
        </form>
        {this.state.error != null &&
          <div className="ui error message"><p>{this.state.error}</p></div>
        }
      </Column>
    </Wrapper>
  }
  handleChange(event) {
    let value = event.target.value
    this.setState(state => {
      state.password = value
      return state
    })
  }
  handleSubmit(event) {
    event.preventDefault()
    let data = new URLSearchParams()
    data.append('password', this.state.password)
    axios({
      maxRedirects: 0,
      method: 'post',
      url: '/auth/signin',
      data: data
    })
    .then(response => {
      this.setState(state => {
        state.error = null
        return state
      })
      // TODO: Maybe actually use the URL returned by the signin redirect.
      this.props.history.push('/')
    })
    .catch(error => {
      let message
      if (error.response) {
        message = error.response.data
      }
      else {
        message = '' + error
      }
      this.setState(state => {
        state.error = message
        return state
      })
    })
  }
}

class AuthSignout extends React.Component {
  componentDidMount() {
    axios.get('/auth/signout')
    this.props.history.push('/auth/signin')
  }
  render() {
    return <div>Signing you out ...</div>
  }
}


export const routes = [
  <Route exact path="/auth/signin" component={withRouter(AuthSignin)}/>,
  <Route exact path="/auth/signout" component={withRouter(AuthSignout)}/>
];
