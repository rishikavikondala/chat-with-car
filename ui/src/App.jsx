import { Component } from 'react';
import axios from 'axios';
import Smartcar from '@smartcar/auth';
import styled from 'styled-components';
import Connect from './components/Connect';
import Vehicle from './components/Vehicle';
import VoiceRecorder from './components/VoiceRecorder';

const Heading = styled.h1`
  font-family: 'Arial', sans-serif;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
`;

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      vehicle: {},
    };

    this.authorize = this.authorize.bind(this);

    this.onComplete = this.onComplete.bind(this);

    this.smartcar = new Smartcar({
      clientId: process.env.REACT_APP_CLIENT_ID,
      redirectUri: process.env.REACT_APP_REDIRECT_URI,
      scope: ["read_vehicle_info", "control_security", "control_navigation", "control_trunk", "control_climate"],
      mode: 'live',
      onComplete: this.onComplete,
    });
  }

  onComplete(err, code, state) {
    console.log(`${process.env.REACT_APP_SERVER}/exchange?code=${code}`)
    return axios
      .get(`${process.env.REACT_APP_SERVER}/exchange?code=${code}`)
      .then(_ => {
        return axios.get(`${process.env.REACT_APP_SERVER}/vehicle`);
      })
      .then(res => {
        this.setState({ vehicle: res.data });
      });
  }

  authorize() {
    this.smartcar.openDialog({ forcePrompt: true });
  }

  render() {
    return (
      <Container>
        <Heading>Chat with Car</Heading>
        {Object.keys(this.state.vehicle).length === 0 ? (
          <Connect onClick={this.authorize} />
        ) : (
          <>
            <Vehicle info={this.state.vehicle} />
            <VoiceRecorder />
          </>
        )}
      </Container>
    );
  }
}

export default App;
