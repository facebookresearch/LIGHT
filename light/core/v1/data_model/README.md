

# LIGHT Data Model

This folder contains the LIGHT project's data acquisition and management system, built on Tornado server and SQlite database.


## Load data from pickle files to database

light_database.py contains two separate methods, *add_environment_data()* and *add_conversation_data()* for loading environment data and conversation data.

#### Parameters
- **pklpath:** ***str, required***
  Path to the database
- **disable_TQDM:** ***bool, optional***
  Option to disable TQDM progress bars when loading data; default is False.

#### Example usage
```python
from parlai_internal.projects.light.v1.data_model.light_database import LIGHTDatabase

with LIGHTDatabase('database.db') as db:
        db.add_environment_data('environment_data.pickle')
        db.add_conversation_data('conversation_data.pickle', disable_TQDM=True)
```

## Starting the server
Use command line argument to pass in the database path

#### Example usage
```bash
$ python parlai_internal/projects/light/v1/data_model/server.py database.db
Server is starting at localhost:80...
```

## APIs
- **<code>GET</code> edits**
	- URL parameters
		- Optional:
			- id=[int]
			- status=[str]; has to be one of 'submitted', 'accepted', 'accepted_one', 'accepted_all', or 'rejected'
			- player=[int]
			- expand=[bool]; default False
	- Example of successful response
		- Code: 200
		- Content: <code>[{
                    "edit_id": edit_id2,
                    "id": base_room,
                    "field": "name",
                    "unedited_value": "room",
                    "edited_value": "name_edit_test2",
                    "player_id": player,
                    "status": "submitted",
                    "type": "base room"
                }]</code>
- **<code>POST</code> edits**
	- Data parameters
		- Required:
			- id=[int]
			- field=[str]
			- edited_value=[str]
			- player=[int]
	- Example of successful response
		- Code: 201
		- Content: <code>{edit_id:1}</code>
- **<code>POST</code> edits/\<edit_id>/accept/\<accept_type>**
	- URL parameters
		- Required:
			- edit_id=[int]
			- accept_type=[str]; one of 'accept', 'accepted_one', 'accepted_all'
	- Example of successful response
		- Code: 200
		- Content: <code>{id:1}</code>
- **<code>POST</code> edits/\<edit_id>/reject**
	- URL parameters
		- Required:
			- edit_id=[int]
	- Example of successful response
		- Code: 200
		- Content: <code>{id:1}</code>
- **<code>GET</code> edits/\<edit_id>**
	- URL parameters
		- Required:
			- edit_id=[int]
	- Example of successful response
		- Code: 200
		- Content: <code>{
                "edit_id": 1,
                "id": base_room,
                "field": "name",
                "unedited_value": "room",
                "edited_value": "name_edit_test",
                "player_id": player,
                "status": "accepted",
                "type": "base room",
            }</code>
- **<code>POST</code> edges**
	- Data parameters
		- Required:
			- room=[int]
		- Optional:
			- objs=[list of int]; default []
			- chars=[list of int]; default []
			- neighbors=[list of int]; default []
			- dry_run = [bool]; default False
	- Example of successful response
		- Code: 200
		- Content: <code>[
                [2, 5, 'ex_contained', 0],
                [2, 6, 'ex_contained', 0],
                [2, 8, 'ex_contained', 0],
                [2, 3, 'neighbor', 1],
            ]</code>
- **<code>GET</code> entities/\<type>**
	- URL parameters
		- Required:
			- type=[str]
		- Optional:
			- search=[str]; default ''
			- expand=[bool]; default True
	- Example of successful response
		- Code: 200
		- Content: <code>[{
		'id': 2, 'name': 'small room',
		'base_id': 1, 'description': 'tiny',
		 'backstory': 'old'
		 }]</code>
- **<code>POST</code> entities/\<type>**
	- URL parameters
		- Required:
			- type=[str]
	- Data parameters
		- Required:
			- Depends on the type of object being created. Use the endpoint <code>entities/\<type>/fields</code> to retrieve the list of fields for a specific type of entity
	- Example of successful response
		- Code: 200
		- Content: 1
- **<code>GET</code> interactions**
	- Data parameters
		- Required:
			- interaction_id=[int]
	- Example of successful response
		- Code: 200
		- Content: <code>{
                'room': rcontent_id1,
                'participants': [{
                        'ID': participant1,
                        'interaction_id': interaction1,
                        'character_id': ccontent_id1,
                        'player_id': player1,
                    }],
                'turns': [{
                        'ID': turn1_1,
                        'interaction_id': interaction1,
                        'turn_number': 0,
                        'turn_time': 1,
                        'interaction_type': 'speech',
                        'utterance_id': utterance1,
                        'action': '',
                        'speaker_id': participant1,
                        'listener_id': None
                    }]
            }</code>
- **<code>POST</code> interactions**
	- Data parameters
		- Required:
			- room=[int]
			- participants=[list of (character_id, player_id)]
			- turns=[list of dictionaries]
	- Example of successful response
		- Code: 200
		- Content: 1
- **<code>GET</code> entities/\<type>/fields**
	- URL parameters
		- Required:
			- type=[str]
	- Example of successful response
		- Code: 200
		- Content: <code>{
		'id': 'integer', 'name': 'text'
		}</code>
- **<code>GET</code> tables/types**
	- Successful response
		- Code: 200
		- Content: <code>['base character', 'character', 'base object', 'object', 'base room', 'room', 'node content', 'interaction', 'utterance', 'participant', 'turn', 'player']</code>
