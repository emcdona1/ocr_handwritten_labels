import time


class Timer:
    def __init__(self, name='generic timer'):
        """ Creates and starts a timer.  Optional parameter gives the timer an identifying name. """
        self.start_time = None
        self.active = False
        self.name: str = name
        self.start()
        self.duration: float = 0

    def start(self, name=None) -> None:
        """ Starts a timer.  Optional parameter to update the timer's name. """
        if self.active:
            print(f'Timer {self.name} already started.')
        else:
            self.start_time = time.time()
            if name:
                self.name = name
            print(f'Timer {self.name} started.')
            self.active = True

    def stop(self) -> None:
        """ Stops the timer and prints the results. """
        end_time = time.time()
        self.duration = end_time - self.start_time
        self.active = False
        self.print_results()

    def print_results(self) -> None:
        """ Prints the completed duration (if stopped) or the current duration (if active). """
        if self.active:
            print(f'Timer {self.name} is still active.  ' +
                  f'Current duration is {time.time() - self.start_time :.1f} seconds.')
        else:
            print(f'Timer completed {self.name} in {self.duration:.1f} seconds.')

    def reset(self) -> None:
        """ Resets the timer.  Does not start it again. """
        self.start_time = None
        self.duration = 0
