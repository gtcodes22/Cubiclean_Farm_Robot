import argparse
import csv
import time
import sys
import os
import socket
import threading
from datetime import datetime

from turtlebot_client.sci_i2c_logger_unified import run_logger, Merge_row_dicts, Set_Headers
from turtlebot_client import odomcsv

def build_sample_name(bed_num, point_num, run_timestamp):
    return f"BED{bed_num}_P{point_num}_{run_timestamp}"

def increment_bed_point(bed_num, point_num):
    if point_num < 6:
        return bed_num, point_num + 1
    return bed_num + 1, 1

def bot_get_readings(bed_num=0, point_num=0, ):
    args = parser.parse_args()
    
    # create one fixed timestamp for the whole run
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    
    # generate csv filename
    csv_name = build_sample_name(bed_num, point_num, run_timestamp)
    CSV_Output_dir="bed_data"
    csv_path = f"{CSV_Output_dir}/{csv_name}.csv"
    
    # create Odom getter thread
    odom_thread = threading.Thread(
        target=odomcsv.main, args=(),
        kwargs={'csv_path':f'{csv_path[:-4]}_odom.csv'})
    odom_thread.name = "Rameez's Script: Odom reading getter"
    odom_thread.daemon = True
    
    #######################################################################
    ####
    #### STAGE 1 - BRANDON'S FUNCTION
    ####
    #######################################################################

    # if valid bed/point numbers are not provided, go with a default of 1,1
    bed_num = bed_num if (bed_num > 0) else 1 
    point_num = point_num if (point_num > 0) else 1

    print(f'i: writing sensor data to {csv_path}')
    
    # run sensor script with standard parameters
    try:
        if not args.test:
            # odom needs to run in parallel with run_logger function
            print('starting odom thread')
            odom_thread.start()
            
            print('starting run_logger function')
            run_logger(
                name=csv_name,
                duration_s=30,
                CSV_Output_dir=CSV_Output_dir,
                Sampling_Period=5.0,
                Min_Sample_Period=5.0,
                ADC_Channel=0,
                ADC_Gain=1
            )
            
        else:
            print('i: test mode! csv will have zero values')
            
            # generate a test csv
            write_test_file(csv_path)
            
    # if the code fails to run, run in test mode
    except Exception as e:
        print(f'exception: run_logger raised {e}, running in test mode! csv will have zero values')
    
        # generate a test csv
        write_test_file(csv_path)
    
    # increment point number to 6, then restart at 1 and increment bed number
    bed_num, point_num = increment_bed_point(bed_num, point_num)
    
    
    #######################################################################
    ####
    #### STAGE 2 - RAMEEZ'S FUNCTION
    ####
    #######################################################################
    # remember to chop off ".csv" file extension when appending _odom.csv
    if args.test:
        print(f'i: writing test odom data to {csv_path[:-4]}_odom.csv')
        write_test_file_odom(f'{csv_path[:-4]}_odom.csv')
    #else:
    #    try:
            #odomcsv.main(f'{csv_path[:-4]}_odom.csv')
    #    except Exception as e:
    #        print(f'exception: odomcsv raised {e}, running in test mode! csv will have zero values')
    #        write_test_file_odom(f'{csv_path[:-4]}_odom.csv')
            
    
    #######################################################################
    ####
    #### STAGE 3 - JADE'S FUNCTION
    ####
    #######################################################################
    # send written csv files to bot_main.py script
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1',1993))
            s.sendall(f'{csv_path},'.encode('utf-8'))
            s.sendall(f'{csv_path[:-4]}_odom.csv'.encode('utf-8'))
    except ConnectionRefusedError:
        print('Connection refused, is bot_main.py running?')
    
    
def write_test_file_odom(csv_path):
    ## stolen from Rameez's script! 😈
    # blank test values
    x_list = [0] * 120
    y_list = [0] * 120
    
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x','y'])
        for x, y in zip(x_list, y_list):
            writer.writerow([x, y])
    print(f"CSV file created with {len(x_list)} samples.")
            
def write_test_file(csv_path):
    ## stolen from Brandon's script! 😈
    headers = Set_Headers()
    
    duration_s = 2.5
    Sampling_Period=0.5
    
    start = time.monotonic()
    end = start + float(duration_s)
    idx = 0
    
    # get directory from csv_path
    CSV_Output_dir = csv_path[:csv_path.rfind('\\')]
    
    print(f'writting to {CSV_Output_dir} dir')
    print(f'csv_path: {csv_path}')
    
    # if the output folder doesn't exist, create it!
    if not os.path.isdir(CSV_Output_dir):
        os.makedirs(CSV_Output_dir)
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        #while time.monotonic() < end:
        for i in range(5):
            #loop_start = time.monotonic()
            idx += 1

            row_base = {
                "index": idx,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "DAQ1_ok": 0,
                "DAQ2_ok": 0,
                "ADC_ok": 0,
                "overrun": 0,
            }

            # -------- DAQ1 --------
            daq1_vals = {"p2.Temp_Air": "", "p2.Humi_Air": "", "p3.CO2": ""}
            v_p2_temp = 0
            v_p2_rh = 0
            v_p3_co2 = 0
            
            t_clean = 0.0
            rh_clean = 0.0
            co2_clean = 0.0

            # -------- DAQ2 --------
            daq2_vals = {"d2.NH3": "", "d2.H2S": ""}
            v_d2_nh3 = 0
            v_d2_h2s = 0
            
            v_ch4 = 0

            validity = {
                "valid_p2_temp": v_p2_temp,
                "valid_p2_rh": v_p2_rh,
                "valid_p3_co2": v_p3_co2,
                "valid_d2_nh3": v_d2_nh3,
                "valid_d2_h2s": v_d2_h2s,
                "valid_ch4_vout": v_ch4,
            }
            
            daq1_vals = {"p2.Temp_Air": 0.0, "p2.Humi_Air": 0.0, "p3.CO2": 0.0}
            daq2_vals = {"d2.NH3": 0.0, "d2.H2S": 0.0}
            
            row = Merge_row_dicts(
                row_base,
                daq1_vals,
                daq2_vals,
                {"CH4_Vout": 0.0},
                validity
            )

            #elapsed = time.monotonic() - loop_start
            #if elapsed > Sampling_Period:
            #    row["overrun"] = 1
            #    _log_err(err_f, f"Time_Out_Err | overrun | elapsed={elapsed:.3f}s period={Sampling_Period:.3f}s")

            writer.writerow(row)
            f.flush()
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", "-t", required=False,action='store_true')
    bot_get_readings()