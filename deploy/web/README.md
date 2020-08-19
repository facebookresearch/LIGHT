# Web

This folder contains resources for the full web deployment of the LIGHT game.

The code for the backend is served via a tornado web server, and the frontend is also served from this tornado server, although
it is first compiled into static content using `npm install` and `npm run build` in the `./builderapp` and `./gameapp` directories in that order

There are two primary applications which are deployed from this folder on the same server - the builder application and the
game application.  The builder application can be accessed by endpoints prefixed with `/builder/`, while the game application's
endpoints will be prefaced with `/game/`.

By default, when running a server and connecting to the host, the default page displayed is the game page.

## Deploying the server

To completely build and deploy the web pages and game, run:

    bash ./deploy.sh

To just build the static web pages, run:

    bash ./build.sh

To just run the web server, run:

    python ./server/run_server.py [--light-model-root light-model-directory] [--port port] [--hostname host] [--data-model-db world-creation-database]

`./config` contains important configurations for the tornado server, while `./config.js` contains similar configs for the static web pages.  If you want to change the
host or the port, both should be changed!

You can then interface with the game through several options below

_**NOTE**_: if your hostname is localhost, you **must** ensure that the connection in Chrome is through `localhost:port/...`  If the initial link takes you to `127.0.0.1:port/...`
you should replace it with `localhost`.  This is to ensure the authentication works properly (i.e ~~127.0.0.1:35494~~ -> localhost:35494)

## Using LIGHT

You can access that game simply at `hostname:port/`, while the world creation tool is hosted at `hostname:port/builder`.  To switch between the game and world builder,
the hyperlink text under the logo will take you there.  To launch the game from the world builder, you must simply have a custom world and use the launch button

If it is your first time playing, you will be asked to login with a username and password.  The username is not important, but as of now the password must be _**LetsPlay**_

Once you are succesfully authenticated, have fun enjoying the world of LIGHT!
