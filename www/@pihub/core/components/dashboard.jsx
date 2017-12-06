import styled from 'styled-components'
import React from 'react'
import {Route} from 'react-router-dom'

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

/*
{%for item in left_menu%}
<a className="item" href="{{item.url}}">
  {%if item.icon%}
  <i className="{{item.icon}} icon"></i>
  {%endif%}
  {{item.name}}
</a>
{%endfor%}

{%for item in right_menu%}
<a className="item" href="{{item.url}}">
  {%if item.icon%}
  <i className="{{item.icon}} icon"></i>
  {%endif%}
  {{item.name}}
</a>
{%endfor%}
*/

class Dashboard extends React.Component {
  constructor(props) {
    super(props)
    this.state = {menuLeft: [], menuRight: []}
  }
  render() {
    return <Wrapper className="full height">
      <div className="toc">
        <div className="ui vertical inverted left visible menu sidebar visible">
          {this.state.menuLeft}
          <div className="right menu">
            {this.state.menuRight}
          </div>
        </div>
      </div>
      <div className="article">
        <div className="ui masthead vertical segment">
          <h1>Dashboard</h1>
        </div>
        {this.props.children}
      </div>
    </Wrapper>
  }
}

export default <Route exact path="/" component={Dashboard}/>
