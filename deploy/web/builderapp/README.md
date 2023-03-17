# LIGHT Data Model UI

This folder contains the LIGHT project's data acquisition and management system UI, built in React.js

## To run

- Make sure port in `src/config.js` is the same as the python server port
- `npm install` and then `npm run build`, then run `npm install` and `npm run build` in `../gameapp`
- Run `../server/run_server.py`, with usage instructions in the parent directory.  Navigate to the endpoint `localhost:port/builder/`

### Bugs/Tasks

- [ ] On review submit, add a dialog with insight into the requests (and ways to signal that one or more may have failed)
- [ ] On edit submit, add a dialog with some insight into the requests in progress (and ways to signal that one or more may have failed)
- [ ] In BaseSuggest Component, be able to create a new base entity through the Suggest createNewItemFromQuery prop
- [ ] Tests currently spam a lot of errors on CI in tests where the API request is not mocked, mock the entire API during testing
- [ ] Explore page pagination, support changing number of results per page
- [ ] Explore page pagination, track page number in url
- World Builder
  - [ ] BaseMultiSelect component in the World Builder currently allows the same entity to be added multiple times, modify the BaseMultiSelect component to disable selected entities
  - [ ] Updating emojis in the advanced editor doesn't immediately update the tile preview, investigate
  - [ ] Support Objects being placed in another Object that is a container
  - [ ] Support Objects that are wearable to be placed in a character
  - [ ] Support doors?



![World Builder ReadMe Diagram](https://user-images.githubusercontent.com/80718342/224455917-3fb008ff-f40c-47b5-acc1-635a1d0fdb17.png)

