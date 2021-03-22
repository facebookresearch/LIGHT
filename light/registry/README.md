# Registry

The LIGHT registry contains all of the information for registering different modules, models, and systems, for use by the other parts of the LIGHT system. It is an abstraction layer on LIGHT that tries to seperate out configuration (especially module-specific configuration) from the rest of the system.

It comprises of a few things, described below:

## Hydra structured config bases

Configuration under-the-hood is handled by Hydra. Classes and utility functions surrounding registering configs to hydra exist in the registry directory. Abstract or base classes that want to mark themselves as configurable should declare a base structured config in their file, and register it via these helpers.

## Model Pool

The largest component of the registry is the model pool, which is initialized during the setup of any LIGHT script. The model pool lets you register models to arbitrary keys, and you can register the same model to multiple keys if desired. There is global access to this pool, so the keys can later be referenced either from LIGHT core code, or from custom classes and implementations of LIGHT base classes.