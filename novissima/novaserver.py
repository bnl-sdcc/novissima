#!/usr/bin/env python 

"""
adding functionalities to the server object
"""

import datetime


# FIXME ???
# should the class inherit from server, instead of containing it???
class NovissimaServer(object):

    def __init__(self, server):
        self.server = server


    def updatedtime(self):
        """
        returns datetime object for the server.updated value
        """
        return datetime.datetime.strptime(self.server.updated, "%Y-%m-%dT%H:%M:%SZ")


    def __cmp__(self, other):
        """
        to sort servers by updated time
        """
        mytime = self.updatedtime()
        othertime = other.updatedtime()
        if mytime > othertime:
            return 1
        elif mytime < othertime:
            return -1
        else:
            return 0




