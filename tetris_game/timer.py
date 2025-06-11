from pygame.time import get_ticks

class Timer: 
    def __init__(self, duration, repeated = False, func = None):
        self.repeated = repeated
        self.duration = duration
        self.func = func

        self.start_time = 0
        self.active = False

    def activate(self):
        """
        Activates the timer, starting the countdown.
        """
        self.start_time = get_ticks()
        self.active = True

    def deactivate(self):
        self.active = False
        self.start_time = 0
    
    def update(self):
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration and self.active:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()
            if self.repeated:
                self.activate()

        