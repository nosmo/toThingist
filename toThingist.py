#!/usr/bin/python

import ConfigParser
import optparse
import json
import sys
import os.path
import tempfile

import todoist

import thingsinterface

"""toThingist - sync between Todoist and Cultured Code's Things"""

BASE_STATE = {"incomplete": [], "complete": [],
              "todoist_to_things": {}, "things_to_todoist": {}}


class ToThingist(object):

    def __init__(self, todoist_obj, things_location, state):
        self.todoist = todoist_obj
        self.things_location = things_location
        self.state = state

    def sync_things_to_todoist(self, verbose=False):

        inbox_id = -1
        for project in self.todoist.getProjects():
            if project["name"] == "Inbox":
                inbox_id = project["id"]

        for todo in thingsinterface.ToDos(self.things_location):
            if todo.thingsid in self.state["things_to_todoist"]:
                todoist_id = self.state["things_to_todoist"][todo.thingsid]
                if todo.is_closed() or todo.is_cancelled():
                    complete_result = self.todoist.setComplete(todoist_id)
                    if verbose:
                        sys.stderr.write(
                            "Marking task '%s' as complete in ToDoist\n" % todo.name
                        )

                if verbose:
                    sys.stderr.write(
                        "Todo %s (\"%s\") synced already\n" % (todo.thingsid, todo.name)
                    )
                continue

            z = self.todoist.createTodo(todo.name, inbox_id)
            todoist_id = z["id"]
            self.state["todoist_to_things"][todoist_id] = todo.thingsid
            self.state["things_to_todoist"][todo.thingsid] = todoist_id

        #TODO better return
        return self.state


    def sync_todoist_to_things(self, tag_import=False,
                               verbose=False):

        """Sync todoist inbox todos into a given Things location.

         Args:
          self.todoist: Todoist object
          statefile: path to the file in which the things/todoist id mapping is stored
          tag_import: tag all imported todos with "todoist_sync"

        """

        for project in self.todoist.getProjects():
            if project["name"] == "Inbox":
                todoist_todos = self.todoist.getAllTodos(project["id"])
                for todoist_todo in todoist_todos:
                    creation_date = todoist_todo["date_added"]
                    name = todoist_todo["content"]
                    todoist_id = str(todoist_todo["id"])

                    if todoist_id in self.state["todoist_to_things"]:
                        if verbose:
                            sys.stderr.write(
                                "Todo %s (\"%s\") synced already\n" % (todoist_id, name)
                            )

                        if todoist_todo["checked"] == 1:
                            # todo is checked off - check off locally
                            to_complete = thingsinterface.ToDo._getTodoByID(
                                self.state["todoist_to_things"][todoist_id])
                            to_complete.complete()
                            if verbose:
                                sys.stderr.write("marked '%s' as complete" % name)

                        continue

                    tags = []
                    if tag_import:
                        tags = ["todoist_sync"]

                    if todoist_todo["checked"] != 1:
                        newtodo = thingsinterface.ToDo(name=name,
                                                       tags=tags,
                                                       location=self.things_location)
                        self.state["todoist_to_things"][todoist_id] = newtodo.thingsid
                        self.state["things_to_todoist"][newtodo.thingsid] = todoist_id
        # TODO better return
        return self.state

def main():
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="Be verbose",
                      action="store_true")
    parser.add_option("-c", "--config",
                      action="store", dest="configpath",
                      default="~/.tothingist",
                      help="alternate path for configuration file")

    (options, args) = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(options.configpath))
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    statefile = os.path.expanduser(config.get("config", "statefile"))
    things_location = config.get("config", "thingslocation")
    todoist_obj = todoist.ToDoist(username, password)

    state = BASE_STATE.copy()
    if statefile and os.path.isfile(statefile):
        state_f = open(statefile)
        try:
            state = json.loads(state_f.read())
        except ValueError:
            print "Failed to open state file! Is it valid JSON?"
            raise SystemExit(1)
        state_f.close()

    tothingist_obj = ToThingist(todoist_obj, things_location, state)

    tothingist_obj.sync_todoist_to_things(tag_import=True,
                                          verbose=options.verbose)
    tothingist_obj.sync_things_to_todoist(verbose=options.verbose)

    if statefile:
        if not tothingist_obj.state:
            sys.stderr.write(("Not writing state file as there is no content"
                              " to sync. This could be in error or you'll need"
                              " to create at least one todo. "))
        else:
            # Avoid zeroing the file when the user's system has no
            # disk space by writing a tempfile
            temp_state_filename = tempfile.mkstemp(text=True)
            with open(temp_state_filename[1], "w") as temp_state_f:
                temp_state_f.write(json.dumps(tothingist_obj.state))
            os.rename(temp_state_filename[1], statefile)

if __name__ == "__main__":
    main()
