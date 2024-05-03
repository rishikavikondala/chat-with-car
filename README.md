## What is this project?

This project allows you to issue voice commands to Internet-enabled vehicles.

Selected as a winner of Anthropic's Build for Claude contest: https://twitter.com/alexalbert__/status/1783604743132365197

## What is the tech stack?

- React UI for sending voice commands. This React UI is purely a prototype interface; in future iterations, I'm aiming to integrate with Siri and/or other voice assistants.
- FastAPI Python backend for processing voice commands.
- [SmartCar API](https://smartcar.com/docs/api-reference/intro) for interacting with vehicles.
    - While I've developed this project specifically with Teslas in mind, I've chosen to use SmartCar to be able to expand to other vehicle manufacturers in the future. Some of the endpoints in the project are specific to Teslas, so please try it out with a Tesla for this initial MVP.
- Whisper API for speech-to-text.
- Claude with tool use.
    - Each available command that can be issued to Claude is provided as a tool in the API request.
    - Claude parses the voice command and maps it to the appropriate tool and arguments.

## Running locally

- Create a Smartcar developer account and create a new project in that account.
- Set the following environment variables (client id and client secret can be found in the Smartcar portal).
```
export OPENAI_API_KEY=<get from OpenAI dashboard>
export ANTHROPIC_API_KEY=<get from Anthropic console>

export SMARTCAR_CLIENT_ID=<get from Smartcar dashboard>
export SMARTCAR_CLIENT_SECRET=<get from Smartcar dashboard>
export SMARTCAR_REDIRECT_URI=https://javascript-sdk.smartcar.com/v2/redirect?app_origin=http://localhost:3000

export REACT_APP_CLIENT_ID=<get from Smartcar dashboard>
export REACT_APP_REDIRECT_URI=https://javascript-sdk.smartcar.com/v2/redirect?app_origin=http://localhost:3000
export REACT_APP_SERVER=http://localhost:8000
```
- In the `ui` directory, run `npm install` and then `npm start`.
- In the `api` directory, run `pip install -r requirements.txt` and then `uvicorn main:app --reload`.
- Go to `localhost:3000`, click the Connect button and go through the Smartcar flow.
- If you are not prompted to do so by default, then visit https://www.tesla.com/_ak/smartcar.com and add Smartcar as a third-party key. See [here](https://smartcar.com/docs/help/oem-integrations/tesla/developers#commands) for more information on why this is needed.

## Future extensions

- Integrate with Siri to remove the need for a React UI for issuing commands.
- Add support for other commands and vehicles.
- General improvements to code quality (error handling, logging, rate limiting, etc.).
- Generalize the code to not be hardcoded for running locally (localhost).
