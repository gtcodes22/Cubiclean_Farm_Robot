class BedData():
    def __init__(self, bednum):
        self.bednum = bednum
        self.timestamp = None
        self.points = [None]*6
    
    def add_point_file(self, index, filename):
        self.points[index - 1] = filename
    
    def set_timestamp(self, time):
        self.timestamp = time
        