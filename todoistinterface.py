#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import ConfigParser
import os.path

import todoist

class ToDoistInterface(object):
    """Ugly wrapper for the ToDoist.com API"""

    def __init__(self, token):
        self.token = token
        self.api = todoist.TodoistAPI(token)
        self.api.sync()

    def get_projects(self):
        '''
        Get all projects.
        '''
        return self.api.projects.all()

    def get_uncompleted_todos(self, project_id):
        '''
        Get all uncompleted todo items.
        '''
        return [ i for i in self.api.items.all() if not i["checked"] ]

    def get_completed_todos(self, project_id):
        '''
        Get all completed todo items.
        '''
        return [ i for i in self.api.items.all() if i["checked"] ]

    def get_all_todos(self, project_id):
        '''
        Get all todo objects.
        '''
        return self.get_uncompleted_todos(project_id) + self.get_completed_todos(project_id)

    def set_complete(self, item_id):
        '''
        Set a todo's state to complete.

         item_id: the todoist ID of the todo.
        '''
        self.api.items.complete([item_id])
        self.api.commit()
        return True

    def create_todo(self, name, project_id):
        '''
        Create a new todo.

         name: the label for the todo item.
         project_id: the id of the project in which to create a todo.
        '''

        add_res = self.api.items.add(name.encode('utf-8'), project_id)
        self.api.commit()
        return add_res

    def get_inbox_id(self):
        '''
        Get the project ID for the Inbox project.
        '''
        return [ i for i in self.get_projects() if i["name"] == "Inbox" ][0]

def main():
    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser("~/.tothingist"))
    api_key = config.get('login', 'api_token')
    a = ToDoistInterface(api_key)
    inbox_id = a.get_inbox_id()
    import pprint
    pprint.pprint(a.get_all_todos(inbox_id["id"]))

if __name__ == "__main__":
    main()
