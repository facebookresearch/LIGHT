# LIGHT Graph

The LIGHT graph is the core state of the environment over which LIGHT takes place. This folder contains the components for managing, building, and operating on Graphs.

## Testing Hack
The following lines should be inserted in starspace_all.py during testing after self.db_path is set:

```
    # manual override for efficency - change this to your scratch, copied from
    # /checkpoint/light/data/databse3.db
    self.db_path = '/scratch/lucaskabela/database3.db'
```
