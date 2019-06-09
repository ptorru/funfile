#################################################################################
#  Copyright (c) 2019 Pedro Torruella
#
# Author: Pedro Torruella
#
# Description: Funfile is a demonstration toy project.
#              It scans the file system from a given starting point. It then
#              uses the file size of the files it detects as an input signal.
#              Then, some DSP algorithms are applied on top of this signal,
#              for demonstration purposes only. We don't envisage any actual
#              application.
#
#              At the moment this is the processing pipeline we have got:
#
#                                                +-------+
#                                                |       |
#                                 +----------+   |  DCT  |   +----------+
#                                 |          +--->       +--->          |
#                                 |   File   |   +-------+   |  Plot    |
#                                 |   scan   |               |  Results |
#                                 |          +--------------->          |
#                                 +----------+               +----------+
#
#
# Resources
# Consulted:
#              [1] https://docs.python.org/3/library/os.html#os.walk
#              [2] https://www.troyfawkes.com/learn-python-multithreading-queues-basics/
#              [3] https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/
#
# Improvements:
#               Exposed certain constants as CLI parameters instead.
#################################################################################

from queue           import Queue
from threading       import Thread
from funfile_classes import scanner
from funfile_classes import dcter
from funfile_classes import plotter

TotalBars = 64
MaxPix= 16
MaxVal= 100000
Step  = MaxVal/MaxPix
Consumers = 2
RefreshRate = 10
WorkDir = '/lib'

if __name__ == '__main__':

    # Creating list for the file scanner.
    # Used to store all the Q's that feed data to all the consumer threads.
    producer_outputs = []
    for i in range(Consumers):
        producer_outputs.append(Queue(maxsize=0))

    # Connection from Producer to DSP-er is done here
    dcter_inputs  = [producer_outputs[1]]
    dcter_outputs = [Queue(maxsize=0)]


    # Connection of queues between threads is done here
    plot_inputs = [{plotter.Q : producer_outputs[0], plotter.Name : "Wave"},
                   {plotter.Q : dcter_outputs[0]   , plotter.Name : "DCT"}]

    # Create thread objects
    scanner = scanner([], producer_outputs, WorkDir, TotalBars)
    dcter = dcter(dcter_inputs,dcter_outputs)
    plotter = plotter(plot_inputs, [], Step, MaxPix, RefreshRate,
                      TotalBars, scanner)

    # Activating all threads
    threads = [scanner, dcter, plotter]
    for thread in threads:
        thread.setDaemon(True)
        thread.start()

    # Wait for all threads to finish
    scanner.join()
    dcter.join()
    for input in plot_inputs:
        input[plotter.Q].join()
