#################################################################################
#  Copyright (c) 2019 Pedro Torruella
#
# Author: Pedro Torruella
#
# Description: Implements Objects that will be used to run each of the
#              threads of the funfile program.
#              * scanner: scans the file system, is the main producer.
#              * dcter: calculates DCT on input data.
#              * plotter: plots results by all producers.
# Resources
# Consulted:
# Improvements:
#               Tidy: Move the inheritance of Threading into the Task class.
#################################################################################

from task       import *
from os         import system as syscall
from os         import walk
from os.path    import join, getsize, isdir
from time       import sleep
from statistics import mean
from threading  import Thread
from dct        import dct

# purpose: Scans the file system, gets file-sizes, builds a list of "TotalBars"
#          elements, and puts this data set into all queues contained
#          in "out_queues".
class scanner(task,Thread):
    def __init__(self,inputs,outputs,base_dir,TotalBars):
        task.__init__(self,inputs,outputs)
        Thread.__init__(self,name=scanner)
        assert type(base_dir) is str and isdir(base_dir)
        self.base_dir = base_dir
        self.status = {'currentDir' : base_dir, 'done': False}
        self.TotalBars = TotalBars

    def run(self):
        data = []
        for root, dirs, files in walk(self.base_dir):
            self.set_status({'currentDir' : root, 'done' : False})
            for name in files:
                sleep(0.1) # We slow down this process to better appreciate
                           # what's going on.
                # Note: API for status can be improved, lest having to
                #       define the whole dictionary on every call.
                current_file=join(root, name)
                if len(data) < self.TotalBars:
                    data.append(getsize(current_file))
                else:
                    data=data[1:]
                    data.append(getsize(join(root, name)))
                    for the_queue in self.outputs:
                        the_queue.put(data)
        self.set_status({'currentDir' : root, 'done' : True})


# purpose: Calls DCT on the incoming data set.
#          We have left open the possibility for the same object to
#          handle multiple input/outputs
class dcter(task, Thread):
    def __init__(self,inputs,outputs):
        assert len(inputs) == len(outputs) and len(inputs) > 0
        task.__init__(self,inputs,outputs)
        Thread.__init__(self,name="dsper")

    def run(self):
        while True:
            for i in range(len(self.inputs)):
                data = self.inputs[i].get(block=True)
                new_data = dct(data)
                self.outputs[0].put(new_data)
                self.inputs[0].task_done()



# purpose: Prints a bar graph on the terminal, given a data-set containing the
#          Y values for each bar.
def print_data(input, top, step, total_bars):
    for element in reversed(range(top)):
        for bar in range(total_bars):
            if input[bar] < (element * step):
                print(" ", end="")
            else:
                print("*", end="")
        print("|")


# purpose: Plots data available on all queues contained in "input".
#          We assume there will always be co-sited elements in these queues.
class plotter(task, Thread):
    Q = 0
    Name = 1
    single_input = {Q : "", Name : ""}
    def __init__(self,inputs,outputs,step,max_pix,refresh_rate,total_bars,scanner):
        task.__init__(self,inputs,outputs)
        Thread.__init__(self,name="plotter")
        self.scanner = scanner
        self.TotalBars = total_bars
        self.RefreshRate = refresh_rate
        self.MaxPix = max_pix
        self.Step = step
        assert len(outputs) == 0
        for elem in inputs:
            assert type(elem) is dict


    def run(self):
        while True:
            sleep(1/self.RefreshRate)
            syscall('clear')

            print('Current dir: ', self.scanner.get_status()['currentDir'])
            print('Has scanner finished?: ', str(self.scanner.get_status()['done']))

            for i in range(len(self.inputs)):
                print(self.inputs[i][plotter.Name])

                data = self.inputs[i][plotter.Q].get(block=True)

                # Assumes that input list was built with DCT input on index 1
                if i == 1:
                    # Adjusting gain
                    the_step = self.Step * self.TotalBars
                else:
                    the_step = self.Step

                print_data(data, self.MaxPix, the_step, self.TotalBars)
                print("The mean is: ", mean(data), )
                print("-------------------------")

                self.inputs[i][plotter.Q].task_done()
