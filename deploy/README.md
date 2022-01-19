# deploy

Folder containing all of the backend and frontend code for deploying an aspect of LIGHT on one of the surfaces we support.


**Subdirectories:**
- **`web`**: Code for the current [light-rpg.ai](https://light-rpg.ai) deploy. Minus some deploy + safety secrets, of course! You'll need to supply your own for a local deployment.
- **`messenger`**: Code for the messenger deploy used in our [LIGHT-WILD](https://arxiv.org/abs/2008.08076) data collection. Not in a deploy-ready state, though the underlying ParlAI worlds contain the same logic we used in those experiments.
