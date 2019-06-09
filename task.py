#################################################################################
#  Copyright (c) 2019 Pedro Torruella
#
# Author: Pedro Torruella
#
# Description: Implements a general Task class, with some support variables
#              that are helpful for our case.
# Resources
# Consulted:
# Improvements:
#               * Defensive programming:
#                 - Add a template for the status, and add a "check_status"
#                   method, to allow checking the new_status dictionary before
#                   assigning it to the instance's status.
#################################################################################

from queue      import Queue
#from threading  import Thread
from threading  import Lock

class task():
    # purpose: class constructor.
    #          inputs: is a list, can be of Queues, or other container
    #          outputs: as inputs.
    def __init__(self,inputs,outputs):
        assert type(inputs) is list and type(outputs) is list
        self.inputs = inputs
        self.outputs = outputs
        self.status = {}
        self.status_lock = Lock()

    # purpose: place holder to be overloaded by child classes.
    def run(self):
        pass

    # purpose: to give access to object's status
    def get_status(self):
        self.status_lock.acquire()
        toreturn = self.status
        self.status_lock.release()
        return toreturn

    # purpose: to allow safely changing the status.
    def set_status(self,new_status):
        self.status_lock.acquire()
        self.status = new_status
        self.status_lock.release()

