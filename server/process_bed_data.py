import os

from bed_webview.Extract_Files import Extract_filename
from server.BedData import BedData

def get_latest_bed_data(rawDataFolder='bed_data',procDataFolder='bed_app_data'):
    # starting at bed 0 point 1
    beds = [None] * 9
    
    bedDataFiles = os.listdir(rawDataFolder)
    
    # if output folders doesn't exist, create them
    if not os.path.isdir(procDataFolder):
        os.makedirs(procDataFolder)
    
    bedProcFiles = os.listdir(rawDataFolder)
    
    for file in bedDataFiles:
        # skip any non-csv files
        if not file.lower().endswith('.csv'):
            continue
            
        print(file)
        bedDict = Extract_filename(file)
        # if extracting the filename fails, continue
        if not bedDict:
            print('could not extract details from filename')
            continue
            
        bedID = int(bedDict['Bed_ID'][3:])
        pointID = int(bedDict['Point_ID'])
        timestamp = bedDict['TimeStamp']
        print(f'[{bedID}][{pointID}] ({timestamp})')
        
        # if there is a file with a newer timestamp, create a new BedData
        # object
        if not beds[bedID] or timestamp > beds[bedID].timestamp:
            beds[bedID] = BedData(bedID)
            beds[bedID].set_timestamp(timestamp)
        
        # if the file timestamp matches the bed timestamp, add point file
        if timestamp == beds[bedID].timestamp:
            beds[bedID].add_point_file(pointID, file)
        
    # for each bed print all the points (should be the latest)
    for bed in beds:
        if bed:
            procFilename = f'BED{bed.bednum}_{bed.timestamp}'
            
            # process the bed data
            if not procFilename in bedProcFiles:
                print(f'processing BED{bed.bednum} (bed.timestamp)')
                process_bed_data(bed)
                
            for i in range(6):
                print(f'{bed.bednum}:{i + 1} - {bed.points[i]}')
    
    # check to see if this bed has already been processed
    
    
    # get mean for each point
    # get mean for whole bed

def process_bed_data(bed : BedData):
    procFilename = f'BED{bed.bednum}_{bed.timestamp}'
    return
    
if __name__ == "__main__":
    process_bed_data()