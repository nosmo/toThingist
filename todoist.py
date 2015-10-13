#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import ConfigParser

class ToDoist(object):
    """Ugly wrapper for the ToDoist.com API"""

    def __request(self, path, args={}):
        '''
         Request a path from ToDoist and decode the JSON.

         path: a path to an object to be requested
         args: a dictionary containing key/value args to be passed via GET
        '''

        BASE_URL = "https://todoist.com/API/"

        if self.token:
            args["token"] = self.token

        webargs = urllib.urlencode(args)
        opened_url = urllib2.urlopen(BASE_URL + path, webargs)
        url_data = opened_url.read()
        results = json.loads(url_data)
        return results

    def __login(self):
        '''
         Log into ToDoist and return the API token.
        '''
        return self.__request(
            "login", {"email": self.__username,
                      "password": self.__password}
        )["api_token"]

    def __init__(self, username, password):
        self.token = None
        self.__username = username
        self.__password = password
        self.token = self.__login()

    def get_projects(self):
        '''
        Get all projects.
        '''
        return self.__request("getProjects")

    def get_uncompleted_todos(self, project_id):
        '''
        Get all uncompleted todo items.
        '''
        return self.__request("getUncompletedItems",
                              {"project_id" : project_id})

    def get_all_todos(self, project_id):
        '''
        Get all todo objects.
        '''
        uncompleted_items = self.__request("getUncompletedItems",
                                           {"project_id" : project_id})
        completed_items = self.__request("getCompletedItems",
                                         {"project_id" : project_id})
        return uncompleted_items + completed_items

    def set_complete(self, item_id):
        '''
        Set a todo's state to complete.

         item_id: the todoist ID of the todo.
        '''
        return self.__request("completeItems", {"ids": [int(item_id)]})

    def create_todo(self, name, project_id):
        '''
        Create a new todo.

         name: the label for the todo item.
         project_id: the id of the project in which to create a todo.
        '''

        return self.__request("addItem", {"project_id": project_id,
                                          "content": name.encode('utf-8')})

def main():
    config = ConfigParser.ConfigParser()
    config.read(".tothingist")
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    a = ToDoist(username, password)
    inbox_id = [ i for i in a.getProjects() if i["name"] == "Inbox" ][0]
    import pprint
    pprint.pprint(a.getAllTodos(inbox_id["id"]))

if __name__ == "__main__":
    main()
