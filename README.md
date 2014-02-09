toThingist
==========

Bidirectional sync between [Things](http://culturedcode.com/things/) and [ToDoist](https://todoist.com).

Requirements
---------
toThingist requires the [pythings](https://github.com/nosmo/pythings) module.

Operation
---------

toThingist.py reads a config file at ```.tothingist```. This file
specifies a few obvious things like username and password for
todoist.com.

The ```statefile``` option is currently used to maintain a mapping
between todoist IDs and things IDs. Use of the state file is not
required but not using it will result in duplication of imported todos
so you should probably use it.

The ```thingslocation``` option is used to indicate where a todo
should go once imported from todoist. (ie "Today", "Inbox" etc)

Running toThingist.py will sync all todos in ```thingslocation``` to
the inbox of the configured Todoist account, and all todos from the
Todoist inbox to ```thingslocation```. The mapping between todos is
maintained in the state file.


Current state
---------

The script can currently sync the Todoist inbox to a list in Things,
and a Things list to the Todoist inbox. Status is not currently
tracked but is the next thing on the list.
