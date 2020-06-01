# LIGHT Data Model UI

This folder contains the LIGHT project's data acquisition and management system UI, built in React.js

## To run

- Obtain a .db file (either by importing a pickle file, or from the FAIR cluster at /private/home/jju/ParlAI/data/light/environment/db/database3.db)
- Run the python server with the db file
- Make sure port in `src/config.js` is the same as the python server port
- `npm start`

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
  - [ ] Determining a structure for storing a world in the database
  - [ ] Support Objects being placed in another Object that is a container
  - [ ] Support Objects that are wearable to be placed in a character
  - [ ] Support doors?
