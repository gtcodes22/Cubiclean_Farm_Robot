from PySide6.QtCore import QObject, QThread, Signal#, pyqtSignal

# class which defines a Matlab Worker Thread
class MatlabWorker(QThread):
    # define signals here
    # Signals can contain multiple types. When we emit a signal we pass variables
    # of those types as arguments. Here are some examples.
    startedProcessing = Signal()
    endedProcessing = Signal()
    graphGenerated = Signal()
    currentProgress = Signal(int) # ← might be good as a visual indicator to end
                                  # user if the processing takes a non-trivial
                                  # time to complete
    
    # an example method, which we could use to pass whatever data is needed to
    # be processed to this object
    def setData(self, data):
        self.data = data

    # this is the function that the worker will execute when started. Think of
    # this like it's own python script
    def run(self):
        # debugging print to assure that this thread is actually running
        print("MW: MatlabWorker started")
        
        # main logic loop
        while True:
            # insert matlab processing code here!
            
            # example code
            for i in range(1000):
                # every 50 iterations emit the "current progress"
                if (i % 50 == 0):
                    self.currentProgress.emit(int(i/10)) # as percentage
        