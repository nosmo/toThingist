#!/usr/bin/python

import ConfigParser
import thingsinterface
import todoist
import json
import sys
import os.path
import pprint

"""toThingist - sync between Todoist and Cultured Code's Things"""

BASE_STATE = {"incomplete": [], "complete": [],
              "todoist_to_things": {}, "things_to_todoist": {} }

def _syncThingsListToTodoist(todoist_obj, listname, statefile=None, tag_import=False):

    state = BASE_STATE.copy()
    if statefile and os.path.isfile(statefile):
        state_f = open(statefile)
        state = json.loads(state_f.read())
        state_f.close()

    todos = thingsinterface.ToDos(listname)
    inbox_id = -1
    for project in todoist_obj.getProjects():
        if project["name"] == "Inbox":
            inbox_id = project["id"]

    for todo in todos.todos:
        if todo.thingsid in state["things_to_todoist"]:
            sys.stderr.write("Todo %s (\"%s\") synced already\n" % (todo.thingsid, todo.name))
            continue

        z = todoist_obj.createTodo(todo.name, inbox_id)
        todoist_id = z["id"]
        state["todoist_to_things"][todoist_id] = todo.thingsid
        state["things_to_todoist"][todo.thingsid] = todoist_id

    if statefile:
        state_f = open(statefile, "w")
        state_f.write(json.dumps(state))
        state_f.close()

def _syncTodoistToThings(todoist_obj, statefile=None, tag_import=False, location="Inbox"):

    """Sync todoist inbox todos into a given Things location.

     Args:
      todoist_obj: Todoist object
      statefile: path to the file in which the things/todoist id mapping is stored
      tag_import: tag all imported todos with "todoist_sync"
      location: The things location to import into

    """

    #TODO add verbose output

    state = BASE_STATE.copy()
    if statefile and os.path.isfile(statefile):
        state_f = open(statefile)
        state = json.loads(state_f.read())
        state_f.close()

    for project in todoist_obj.getProjects():
        if project["name"] == "Inbox":
            uncompleteds = todoist_obj.getUncompletedTodos(project["id"])
            for uncompleted in uncompleteds:
                creation_date = uncompleted["date_added"]
                name = uncompleted["content"]
                todoist_id = str(uncompleted["id"])

                if todoist_id in state["todoist_to_things"]:
                    sys.stderr.write("Todo %s (\"%s\") synced already\n" % (todoist_id, name))
                    #TODO check state etc etc
                    # for now, just check whether it exists
                    continue

                tags = []
                if tag_import:
                    tags = ["todoist_sync"]
                newtodo = thingsinterface.ToDo(name, tags=tags, location=location)
                #state["todoist_to_things"][todoist_id] = newtodo.thingsid
                state["things_to_todoist"][newtodo.thingsid] = todoist_id

    if statefile:
        state_f = open(statefile, "w")
        state_f.write(json.dumps(state))
        state_f.close()

def main():
    config = ConfigParser.ConfigParser()
    login_f = config.read(".tothingist")
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    state_file = os.path.expanduser(config.get("config", "statefile"))
    things_location = config.get("config", "thingslocation")
    todoist_obj = todoist.ToDoist(username, password)
    _syncTodoistToThings(todoist_obj, statefile=state_file, tag_import=True,
                         location=things_location)
    _syncThingsListToTodoist(todoist_obj, statefile=state_file, tag_import=True,
                             location=things_location)

if __name__ == "__main__":
    main()
