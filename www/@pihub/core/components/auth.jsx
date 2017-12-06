import styled from 'styled-components'
import React from 'react'
import {Route} from 'react-router-dom'

import logo from '@pihub/core/logo.png'


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

class AuthComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {error: null}
    this.handleSubmit = this.handleSubmit.bind(this)
  }
  render() {
    let error = this.state.error
    return <Wrapper className="ui middle aligned center aligned grid">
      <Column className="column">
        <h2 className="ui teal image header">
          <Image src={logo}/>
          <div className="content">
            PiHub Authentication
          </div>
        </h2>
        <form className="ui large form" method="post" action="">
          <div className="ui stacked segment">
            <div className="field">
              <div className="ui left icon input">
                <i className="lock icon"></i>
                <input type="password" name="password" placeholder="Password" autoFocus/>
              </div>
            </div>
            <div className="ui fluid large teal submit button" onClick={this.handleSubmit}>Submit</div>
          </div>
        </form>
        {error != null &&
          <div className="ui error message"><p>{error}</p></div>
        }
      </Column>
    </Wrapper>
  }
  handleSubmit() {
    console.log('Login!')
    //$('.ui .form').submit()
  }
}

export default <Route exact path="/auth/signin" component={AuthComponent}/>
