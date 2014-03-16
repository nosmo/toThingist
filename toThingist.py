#!/usr/bin/python

import ConfigParser
import optparse
import json
import sys
import os.path
import pprint

import todoist

import thingsinterface

"""toThingist - sync between Todoist and Cultured Code's Things"""

BASE_STATE = {"incomplete": [], "complete": [],
              "todoist_to_things": {}, "things_to_todoist": {} }

def _syncThingsListToTodoist(todoist_obj, listname, state,
                             tag_import=False, verbose=False):

    todos = thingsinterface.ToDos(listname)
    inbox_id = -1
    for project in todoist_obj.getProjects():
        if project["name"] == "Inbox":
            inbox_id = project["id"]

    for todo in todos.todos:
        if todo.thingsid in state["things_to_todoist"]:
            todoist_id = state["things_to_todoist"][todo.thingsid]
            if todo.todo_object.status() == thingsinterface.STATUS_MAP["closed"] or\
               todo.todo_object.status() == thingsinterface.STATUS_MAP["cancelled"]:
                complete_result = todoist_obj.setComplete(todoist_id)
                if verbose:
                    sys.stderr.write("Marking task '%s' as complete in ToDoist\n" % todo.name)

            if verbose:
                sys.stderr.write("Todo %s (\"%s\") synced already\n" % (todo.thingsid, todo.name))
            continue

        z = todoist_obj.createTodo(todo.name, inbox_id)
        todoist_id = z["id"]
        state["todoist_to_things"][todoist_id] = todo.thingsid
        state["things_to_todoist"][todo.thingsid] = todoist_id

    return state

def _syncTodoistToThings(todoist_obj, state, tag_import=False,
                         location="Inbox", verbose=False):

    """Sync todoist inbox todos into a given Things location.

     Args:
      todoist_obj: Todoist object
      statefile: path to the file in which the things/todoist id mapping is stored
      tag_import: tag all imported todos with "todoist_sync"
      location: The things location to import into

    """

    for project in todoist_obj.getProjects():
        if project["name"] == "Inbox":
            todoist_todos = todoist_obj.getAllTodos(project["id"])
            for todoist_todo in todoist_todos:
                creation_date = todoist_todo["date_added"]
                name = todoist_todo["content"]
                todoist_id = str(todoist_todo["id"])

                if todoist_id in state["todoist_to_things"]:
                    if verbose:
                        sys.stderr.write("Todo %s (\"%s\") synced already\n" % (todoist_id, name))

                    if todoist_todo["checked"] == 1:
                        #todo is checked off - check off locally
                        to_complete = thingsinterface.ToDo._getTodoByID(
                            state["todoist_to_things"][todoist_id])
                        to_complete.complete()
                        if verbose:
                            sys.stderr.write("marked '%s' as complete" % name)

                    continue

                tags = []
                if tag_import:
                    tags = ["todoist_sync"]

                if todoist_todo["checked"] != 1:
                    newtodo = thingsinterface.ToDo(name=name, tags=tags, location=location)
                    state["todoist_to_things"][todoist_id] = newtodo.thingsid
                    state["things_to_todoist"][newtodo.thingsid] = todoist_id
    return state

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
    login_f = config.read(os.path.expanduser(options.configpath))
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    statefile = os.path.expanduser(config.get("config", "statefile"))
    things_location = config.get("config", "thingslocation")
    todoist_obj = todoist.ToDoist(username, password)

    state = BASE_STATE.copy()
    if statefile and os.path.isfile(statefile):
        state_f = open(statefile)
        state = json.loads(state_f.read())
        state_f.close()

    state = _syncTodoistToThings(todoist_obj, state, tag_import=True,
                                 location=things_location, verbose=options.verbose)
    state = _syncThingsListToTodoist(todoist_obj,
                                     things_location, state, tag_import=True,
                                     verbose=options.verbose)

    if statefile:
        state_f = open(statefile, "w")
        state_f.write(json.dumps(state))
        state_f.close()

if __name__ == "__main__":
    main()
