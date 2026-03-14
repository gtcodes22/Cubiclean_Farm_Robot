class TurtleBot():
    def __init__(self):
        self.closing = False
        self.batteryLife = 67
        
    # functions that need developing
    def get_battery_life(self):
        return self.batteryLife

    # get speed in cm/s
    def get_speed_cm_ps(self):
        return 15

    # get progress in percentage
    def get_progress(self):
        return 50