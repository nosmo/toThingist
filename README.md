toThingist
==========

Bidirectional sync between Things and ToDoist

Requirements
---------
toThingist requires the [pythings](https://github.com/nosmo/pythings) module.

Operation
---------

toThingist.py reads a config file at ```.tothingist```. This file
specifies a few obvious things like username and password. The state
file is currently used to maintain a mapping between todoist IDs and
things IDs. Use of the state file is not required but not using it
will result in duplication of imported todos so you should probably
use it.

The "thingsdestination" option is used to indicate where a todo should
go once imported from todoist. (ie "Today", "Inbox" etc)


Current state
---------

The script can currently sync from todoist inbox to an arbitrary
Things location.
