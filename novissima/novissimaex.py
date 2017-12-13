#!/usr/bin/env python

# =============================================================================
#
#           Exception classes for novissima
#
# =============================================================================



class ConfigurationFailure(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value


class NovissimaServerCreationTimeOut(Exception):
    def __init__(self, task, timout):
        self.value = 'task %s timed out after %s seconds.' %(task, timeout)
    def __str__(self):
        return self.value


class NovissimaServerCreationFailure(Exception):
    def __init__(self):
        self.value = "creating server failed"
    def __str__(self):
        return self.value
