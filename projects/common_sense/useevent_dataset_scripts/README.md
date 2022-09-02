# Common Sense Scripts

This folder contains ad-hoc scripts to pull data from mephisto and generate summaries/more formal datasets.

### Use-X-With-Y Scripts

These scripts concern the use-x-with-y dataset and generate the dataset used for teachers. They also create some summary statistics to give you a better idea of the state of the dataset.
 
* `get_use_event_dataset_from_mephisto.py`: gets raw 'use-x-with-y' task data from mephisto and saves a dataset with splits
* `use_event_utils.py`: for cleanliness includes some methods to help parse the use-x-with-y dataset to get the information needed for teachers. The data created should be able to be directly added to the graph of the teacher and simulated during setup.
* `examine_saved_use_event_dataset.py`: creates some summary tables from the dataset created with the previous `get_use_event_dataset_from_mephisto` script. Right now it just does counts but could be expanded to do number of unique objects, length of data points, etc.