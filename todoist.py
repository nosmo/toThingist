#!/usr/bin/env python

import urllib2
import urllib
import json
import ConfigParser

class ToDoist(object):
    """Ugly wrapper for the ToDoist.com API"""

    def __request(self, path, args={}):

        BASE_URL = "https://todoist.com/API/"

        if self.token:
            args["token"] = self.token

        webargs = urllib.urlencode(args)
        opened_url = urllib2.urlopen(BASE_URL + path, webargs)
        url_data = opened_url.read()
        results = json.loads(url_data)
        return results

    def __login(self):
        return self.__request(
            "login", {"email": self.__username,
                      "password": self.__password}
        )["api_token"]

    def __init__(self, username, password):
        self.token = None
        self.__username = username
        self.__password = password
        self.token = self.__login()

    def getProjects(self):
        return self.__request("getProjects")

    def getUncompletedTodos(self, project_id):
        return self.__request("getUncompletedItems", {"project_id" : project_id})

    def getAllTodos(self, project_id):
        uncompleted_items = self.__request("getUncompletedItems", {"project_id" : project_id})
        completed_items = self.__request("getCompletedItems", {"project_id" : project_id})
        return uncompleted_items + completed_items

    def setComplete(self, item_id):
        return self.__request("completeItems", {"ids": [int(item_id)]})

    def createTodo(self, name, project_id):
        return self.__request("addItem", {"project_id": project_id,
                                          "content": name})

def main():
    config = ConfigParser.ConfigParser()
    login_f = config.read(".tothingist")
    username = config.get('login', 'username')
    password = config.get('login', 'password')
    a = ToDoist(username, password)
    inbox_id = [ i for i in a.getProjects() if i["name"] == "Inbox" ][0]
    import pprint
    pprint.pprint( a.getAllTodos(inbox_id["id"]))

if __name__ == "__main__":
    main()
