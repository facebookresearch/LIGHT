## Description

Task for the Custom World Interactions task (WIP)

### Folders

- **src/**: contains the react frontend components that comprise the frontend, as well as the css and main javascript file that ties it all together. Of these, the `src/app.jsx` file is currently the most interesting as it displays the landing page.

### Files

The rest of the files are associated with the process of building the finalized javascript main via node and outputting it into the server directory.

- **.babelrc**: links presets and plugins required for babel to transpile the react jsx files into pure js.
- **package.json**: contains the build dependencies and directs the main build process to run the contents of the webpack config file.
- **webpack.config.js**: configures webpack to grab the contents of the `dev` folder and output the final built file to `server/static`.
