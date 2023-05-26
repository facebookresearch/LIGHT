# LIGHT Frontend

This project shares the same run scripts as `create-react-app`.

[See here for more information.](https://facebook.github.io/create-react-app/docs/available-scripts)

## Building the Landing App

The files in this folder host the frontend for the interactive LIGHT game.  To run, be sure to first fun
`npm install` and `npm run build` in `../landingapp`, then run `npm install` and `npm run build` in this
directory.  Then, with the static files build. navigate to `../server/run_server.py`, with usage instructions
in the readme in the parent directory.

## Getting Started
For local deployment with no models. While in the LIGHT directory enter the following commands

```
cd deploy/web
zsh build.sh local-no-models
zsh deploy.sh local-no-models
```
Leave the server running an open a new terminal tab/window Enter the following commands.

```
cd deploy/web/landingapp
npm i
npm start
```

An local instance of the landing app should open in the browser.
*Note: The react app must be accessed using the same browser that was used to login from the initial local-no-models server.


![Landing App ReadMe Diagram](https://user-images.githubusercontent.com/80718342/224455762-06783849-276e-4f2b-89ad-deeec10c572d.png)
