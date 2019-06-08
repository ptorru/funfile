########################################################################################################################
#  Copyright (c) 2019 Pedro Torruella
#
# Author: Pedro Torruella
#
# Description: Funfile is a demonstration toy project.
#              It scans the file system from a given starting point. It then uses the
#              file size of the files it detects as an input signal. Then, some DSP
#              algorithms are applied on top of this signal, for demonstration purposes
#              only. We don't envisage any actual application.
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
########################################################################################################################

from os         import system as syscall
from os         import walk
from os.path    import join, getsize
from queue      import Queue
from threading  import Thread
from time       import sleep
from dct        import dct
from statistics import mean

TotalBars = 64
MaxPix= 16
MaxVal= 1000000
Step  = MaxVal/MaxPix
Processes = 2
RefreshRate = 10

# Constants to index an array
Q = 0
Name = 1

# purpose: Scans the file system, gets file-sizes, builds a list of "TotalBars" elements,
#          and puts this data set into all queues contained in "out_queues".
def get_sizes(start, out_queues):
    data = []
    for root, dirs, files in walk(start):
        for name in files:
            if len(data) < TotalBars:
                data.append(getsize(join(root, name)))
            else:
                data=data[1:]
                data.append(getsize(join(root, name)))

                for the_queue in out_queues:
                    the_queue.put(data)

# purpose: Calls DCT on the incoming data set.
def do_dct(in_queue,out_queue):
    while True:
        data = in_queue.get(block=True)
        new_data = dct(data)
        out_queue.put(new_data)
        in_queue.task_done()

# purpose: Prints a bar graph on the terminal, given a data-set containing the
#          Y values for each bar.
def print_data(input, top, step):
    for element in reversed(range(top)):
        for bar in range(TotalBars):
            if input[bar] < (element * step):
                print(" ", end="")
            else:
                print("*", end="")
        print("|")


# purpose: Plots data available on all queues contained in "input".
#          We assume there will always be co-sited elements in these queues.
def plot(queues):
    while True:
        sleep(1/RefreshRate)
        syscall('clear')

        # We are betting on being lucky, that python will try the queues
        # always in the same order. We know this is not true though, wouldn't
        # do it in production code.
        for i in range(len(queues)):

            the_name = queues[i][Name]
            print(the_name)
            data = queues[i][Q].get(block=True)

            if i == 1:
                the_step = Step * 10
            else:
                the_step = Step

            print_data(data, MaxPix, the_step)
            print("The mean is: ", mean(data), )
            print("-------------------------")

            queues[i][Q].task_done()



if __name__ == '__main__':

    # Building up dictionary containing Queues and descriptors for
    # the plot thread.
    plot_inputs = {}
    for i in range(Processes):
        if i == 1:
            name = "DCT"
        else:
            name = "input"
        plot_inputs[i] = [Queue(maxsize=0), "Graph" + str(name)]

    # Creating input Q for the DCT thread.
    dct_input = Queue(maxsize=0)

    # Creating list for the file scanner (this, the father thread).
    # Used to store all the input Q's for all the child threads.
    producer_outputs = []
    producer_outputs.append(plot_inputs[0][Q])
    producer_outputs.append(dct_input)

    # Creating DCT thread
    worker = Thread(target=do_dct, args=(dct_input,plot_inputs[1][Q],))
    worker.setDaemon(True)
    worker.start()

    # Creating Plotter thread
    worker = Thread(target=plot, args=(plot_inputs,))
    worker.setDaemon(True)
    worker.start()

    # Starting File-Scanner
    get_sizes('/opt', producer_outputs)

    # Wait for all data going into the last thread to be consumed.
    for input in plot_inputs.keys():
        plot_inputs[input][0].join()