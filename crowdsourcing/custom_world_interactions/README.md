# Custom World Interactions (Use-X-With-Y) - Crowdsourcing Tasks

This folder contains the 4 tasks used to generate the use-x-with-y dataset. The goal of this dataset is to expand the types of actions we can simulate in LIGHT to include more "use x object with y object" interactions. This is currently used to expand our action set for common sense teachers and introduce more interesting narrations (compared to our game-engine generated narrations which are very formulaic).

The following folders correspond to each of the tasks, which need to be run in sequence (the overall task if very long, so we split each set of questions into its own task).

The order of tasks is:
1. `collect_narrations`
2. `ground_events`
3. `ground_attributes`
4. `ground_constraints`

Within each folder should be two files of note: `run_task.py`, and `examine_results.py`. 

`run_task.py` handles actually running the mephisto task, and can be run locally (default) or deployed with a command like `python run_task.py mephisto.provider.requester_name=REQUESTER_NAME mephisto.architect.profile_name=mephisto-router-iam mephisto/architect=ec2 conf=use_workers`. Variables at the top of `run_task.py` control where the input data comes from, previous tasks to compare against, and worker lists. (Note these can be moved to config files eventually but as they change a lot it can be easier to see them used in context)

`examine_results.py` helps you explore the results after running a task, and accept/reject units. This doesn't generate any summary dataset tables, for that go to `projects/common_sense/scripts/examine_saved_use_event_dataset.py`

## How to Collect More Data

For each task (in the order listed above) within their respective directories:
* create a new yaml file or change the `use_workers.yaml` file within `hydra_configs/conf/` to fits your needs
* edit the arguments at the top of `run_task.py` to change the input tasks, worker lists, etc.
* Run `python run_task.py mephisto.provider.requester_name=REQUESTER_NAME mephisto.architect.profile_name=mephisto-router-iam mephisto/architect=ec2 conf=use_workers` with your yaml and requester name
* Wait for data collection
* Run `examine_results.py` to accept/reject data and add filters as desired
* Continue to next task

## collect_narrations

This is the most distinct task, where users decide which objects to combine and give us an initial action+narration pair. This task tends to be pretty easy to collect good data with, and simple length filters usually give acceptance rates. 

### _Task Outputs_

* Objects 1 and 2, where 1 is considered the "primary" object
* Simple action phrase, like "clean gold with cloth"
* Narration, a first person description of the action and its result


### _Things to look out for when annotating_

When examining the data keep in mind that the narrations need to be relevant for almost any context, as workers often include backstory that is very situation dependent. For example, in the narration "you swing your axe at the tree, like your brother did before he passed away" the brother isn't something we can easily set as a constraint.

## ground_events

This task is the first of the three "grounding" tasks that take the objects and action-narration pair and create the use-event that we could simulate within LIGHT. 

### _Task Outputs_

* 3rd person narration, where the actors, objects, and locations are highlighted (replaced with standardized names)
* Which objects are removed, if applicable
* Any new object descriptions, if applicable
* A created object, if applicable
* Any new object locations, if applicable

### _Things to look out for when annotating_

This is one of the longer tasks for workers to do, and includes a lot of optional fields. Whether or not the 3rd person narration is valid and highlighted is usually a good filter for overall quality, but workers still often don't fill in created objects or changed locations since it takes more time.

## ground_attributes

This task adds attributes (things that become true or false after the action) and constraints (things that must be true or false for action to take place) to our use-events. 

### _Task Outputs_

* List of attributes
* List of constraints
* Does the narration include information that cannot be included in attributes/constraints?

### _Things to look out for when annotating_

The main problems we have with this task are workers not producing many attributes/constraints and the ones they produce being uninteresting. 

## ground_constraints

This is the final task for our use-event data collection, and collects some extra information needed to simulate the events in LIGHT.

### _Task Outputs_

* How many times this action can be done (infinite, once, a few times)
* Location constraint

### _Things to look out for when annotating_

The biggest error workers make is misunderstanding the times-remaining question, thinking that simple actions (like putting x on y) can be done an infinite number of times. However, as putting x on y changes the location of x, it **can only be once**. We've added some clarifying instructions and wording which seems to help this issue, but errors in this task can be hard to filter so extra care is often needed. 

