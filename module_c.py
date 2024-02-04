import time
from threading import Thread


class ModuleC:
    #  The class responsible for the C module of the application
    def __init__(self):
        self.parameter_a = 0  # parameter from device A
        self.parameter_b = 0  # parameter from device B
        self.result = 0  # the result of the calculation activities of module C
        self.running = False

    def start(self):
        # start calculation
        self.running = True
        thread = Thread(target=self._run)
        thread.start()

    def stop(self):
        # stop calculation
        self.running = False

    def _run(self):
        while self.running:
            self.calculation()
            time.sleep(0.1)  # perform calculations every 100 ms

    def calculation(self):
        #  function responsible for calculations, for the task only adds numbers
        self.result = int(self.parameter_a) + int(self.parameter_b)

