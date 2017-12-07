import styled from 'styled-components'
import React from 'react'
import {Link, Route} from 'react-router-dom'

export const menu = [{
  'url': '/',
  'text': 'Dashboard',
  'icon': 'dashboard'
}]

const Wrapper = styled.div`
  display: flex;
  flex-direction: row;

  > .article {
    margin-left: 260px;
    margin-right: 1em;
    flex: 1;
    padding: 1em;
  }
`

export class Dashboard extends React.Component {
  constructor(props) {
    super(props)
  }
  render() {
    return <Wrapper className="full height">
      <div className="toc">
        <div className="ui vertical inverted left visible menu sidebar visible">
          {menu.map(item => {
            return <Link key={item.url} to={item.url} className="item"><i className={'icon ' + item.icon}/>{item.text}</Link>
          })}
        </div>
      </div>
      <div className="article">
        <div className="ui masthead vertical segment">
          <h1>{this.props.title || 'Dashboard'}</h1>
        </div>
        {this.props.children}
      </div>
    </Wrapper>
  }
}

export default {
  menu,
  Dashboard,
  routes: [
    <Route exact path="/" component={Dashboard}/>
  ]
}
