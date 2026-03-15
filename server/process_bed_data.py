import os
import csv

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
            procFilename = f'BED{bed.bednum}_{bed.timestamp}.csv'
            
            # check to see if this bed has already been processed and
            # process the bed data if not
            if not procFilename in bedProcFiles:
                print(f'processing BED{bed.bednum} ({bed.timestamp})')
                process_bed_data(bed, rawDataFolder, procDataFolder)
                
            for i in range(6):
                print(f'{bed.bednum}:{i + 1} - {bed.points[i]}')
    
    
    
    # get mean for each point
    # get mean for whole bed

def process_bed_data(bed : BedData, rawDataFolder='bed_data', procDataFolder='bed_app_data'):
    procFilename = f'{procDataFolder}/BED{bed.bednum}_{bed.timestamp}.csv'
    procFile = open(procFilename, 'w', newline='')
    procFileWritter = csv.writer(procFile, delimiter=',')
    
    procFileWritter.writerow(['Point', 'Temp_Air', 'Humi_Air', 'CO2_ppm', 'NH3_ppm', 'H2S_ppm', 'CH4_Vout'])
    
    for i in range(6):
        with open(f'{rawDataFolder}/{bed.points[i]}', newline='') as pointFile:
            pointRows = csv.reader(pointFile)
            
            # skip headings row
            pointFile.readline()
            
            readings = 0
            missingReadings = [0] * 6
            
            Temp_Air = 0.0
            Humi_Air = 0.0
            CO2_ppm = 0.0
            NH3_ppm = 0.0
            H2S_ppm = 0.0
            CH4_Vout = 0.0
            
            # sum values together
            for row in pointRows:
                try:
                    # check all readings are there
                    for item in row:
                        float(item)
                        
                    Temp_Air += float(row[0])
                    Humi_Air += float(row[1])
                    CO2_ppm  += float(row[2])
                    NH3_ppm  += float(row[3])
                    H2S_ppm  += float(row[4])
                    CH4_Vout += float(row[5])
                    readings += 1
                except ValueError:
                    # skip any rows that has a missing reading
                    print('process_bed_data: skipping row')
                    continue
            
            # get mean of values
            Temp_Air /= readings
            Humi_Air /= readings 
            CO2_ppm  /= readings
            NH3_ppm  /= readings
            H2S_ppm  /= readings
            CH4_Vout /= readings
            
            # write output to processed data file
            procFileWritter.writerow([i, Temp_Air, Humi_Air, CO2_ppm, NH3_ppm, H2S_ppm, CH4_Vout])
    
    procFile.flush()
    procFile.close()
    
if __name__ == "__main__":
    process_bed_data()