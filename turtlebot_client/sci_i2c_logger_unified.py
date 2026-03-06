#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import argparse
import csv
import re
import time
from datetime import datetime

import DFRobot_RP2040_SCI as sci
import board
import busio
import adafruit_ads1x15.ads1115 as ADS


# I2C ADDRESSES 
DAQ1_I2C_ADDR = 0x21
DAQ2_I2C_ADDR = 0x22
ADC_ADDR = 0x48


# ADS1115 VOLTS CONVERSION 
FS_V = {
    2/3: 6.144,
    1: 4.096,
    2: 2.048,
    4: 1.024,
    8: 0.512,
    16: 0.256
}


def _timestamp_ms():
    # timestamp with ms
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def strip_leading_time(s):
    # removes "hh:mm:ss "
    if len(s) >= 9 and s[2] == ":" and s[5] == ":" and s[8] == " ":
        return s[9:]
    return s


def _log_err(err_f, msg):
    err_f.write(f"{_timestamp_ms()}  {msg}\n")
    err_f.flush()


def Validate_Value(value, min_v=None, max_v=None):
    if value is None:
        return "", 0
    try:
        v = float(value)
    except Exception:
        return "", 0

    if min_v is not None and v < min_v:
        return "", 0
    if max_v is not None and v > max_v:
        return "", 0

    return v, 1


def Merge_row_dicts(*dicts_in):
    out = {}
    for d in dicts_in:
        out.update(d)
    return out


def Set_Headers():
    return [
        "index",
        "timestamp",

        # DAQ1
        "p2.Temp_Air",
        "p2.Humi_Air",
        "p3.CO2",

        # DAQ2
        "d2.NH3",
        "d2.H2S",

        # ADC methane
        "CH4_Vout",

        # validity flag
        "valid_p2_temp",
        "valid_p2_rh",
        "valid_p3_co2",
        "valid_d2_nh3",
        "valid_d2_h2s",
        "valid_ch4_vout",

        # device ok  
        "DAQ1_ok",
        "DAQ2_ok",
        "ADC_ok",

        # timing (timeout>5s) 
        "overrun",
    ]


def _counts_to_volts(counts, gain):
    fs = FS_V.get(gain, 4.096)
    #signed 16-bit single-ended 
    return (int(counts) / 32767.0) * fs


def _parse_daq1_eall(raw, err_f):
    """
    Keep:
     first Temp_Air   p2.Temp_Air
     first Humi_Air   p2.Humi_Air
     CO2              p3.CO2
    Ignore the second Temp_Air (the one from the CO2 sensor dont need both).
    """
    out = {"p2.Temp_Air": None, "p2.Humi_Air": None, "p3.CO2": None}

    if not raw:
        _log_err(err_f, "DAQ1 empty eALL")
        return out

    text = strip_leading_time(raw)
    tokens = [t.strip() for t in text.split(",") if t.strip()]

    temp_air_seen = 0
    humi_air_seen = 0

    for token in tokens:
        m = re.match(r"^([A-Za-z0-9_]+)\s*:\s*([-+]?\d+(?:\.\d+)?)", token)
        if not m:
            continue
        name, val_s = m.group(1), m.group(2)

        try:
            val = float(val_s)
        except Exception:
            continue

        if name == "Temp_Air":
            temp_air_seen += 1
            if temp_air_seen == 1:
                out["p2.Temp_Air"] = val
        elif name == "Humi_Air":
            humi_air_seen += 1
            if humi_air_seen == 1:
                out["p2.Humi_Air"] = val
        elif name == "CO2":
            out["p3.CO2"] = val

    if out["p2.Temp_Air"] is None or out["p2.Humi_Air"] is None or out["p3.CO2"] is None:
        _log_err(err_f, f"DAQ1  incomplete parse  raw='{raw}'  parsed={out}")

    return out


def _map_data(text, wanted=None):
    out = {}
    for token in text.split(","):
        token = token.strip()
        m = re.match(r"^\s*([A-Za-z0-9_]+)\s*:\s*([-+]?\d+(?:\.\d+)?)", token)
        if not m:
            continue
        name, val_s = m.group(1), m.group(2)
        if wanted and name not in wanted:
            continue
        try:
            out[name] = float(val_s)
        except Exception:
            pass
    return out


def _read_daq2(dev2, err_f):
    try:
        raw = dev2.get_information(dev2.eALL, True)
    except Exception as e:
        _log_err(err_f, f"DAQ1 eALL exception  {repr(e)}")
        return None, None, ""

    if not raw:
        _log_err(err_f, "DAQ2  empty eALL")
        return None, None, ""

    stripped = strip_leading_time(raw)
    parsed = _map_data(stripped, wanted=["NH3", "H2S"])

    nh3 = parsed.get("NH3")
    h2s = parsed.get("H2S")

    if nh3 is None or h2s is None:
        _log_err(err_f, f"DAQ2  incomplete parse raw='{raw}' parsed={parsed}")

    return nh3, h2s, raw


def Read_ADC_Methane(ads, ADC_Channel, ADC_Gain, err_f):
    try:
        try:
            ads.gain = ADC_Gain
        except Exception as e:
            _log_err(err_f, f"ADC set gain failed  gain={ADC_Gain} {repr(e)}")

        raw_counts = ads.read(ADC_Channel)
        v = _counts_to_volts(raw_counts, ADC_Gain)

        fs = FS_V.get(ADC_Gain, 4.096)
        v_clean, v_ok = Validate_Value(v, min_v=0.0, max_v=fs)
        if v_ok == 0:
            _log_err(err_f, f"ADC | invalid volts | ch={ADC_Channel} raw={raw_counts} v={v}")

        return v_clean, v_ok

    except Exception as e:
        _log_err(err_f, f"ADC | read exception | ch={ADC_Channel} | {repr(e)}")
        return "", 0


def Check_Device_connection(err_f):
    dev1 = sci.DFRobot_RP2040_SCI_IIC(DAQ1_I2C_ADDR)
    while dev1.begin() != 0:
        _log_err(err_f, "DAQ1  begin failed, retrying 1s")
        time.sleep(1)

    dev2 = sci.DFRobot_RP2040_SCI_IIC(DAQ2_I2C_ADDR)
    while dev2.begin() != 0:
        _log_err(err_f, "DAQ2  begin failed, retrying 1s")
        time.sleep(1)

    try:
        dev1.set_refresh_rate(dev1.eRefreshRate1s)
    except Exception:
        pass

    try:
        dev2.set_refresh_rate(dev2.eRefreshRate1s)
    except Exception:
        pass

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c, address=ADC_ADDR)

    return dev1, dev2, ads


def run_logger(
    *,
    name,
    duration_s,
    CSV_Output_dir="out",
    Sampling_Period=5.0,
    Min_Sample_Period=5.0,
    ADC_Channel=0,
    ADC_Gain=1
):
    if Sampling_Period < Min_Sample_Period:
        Sampling_Period = Min_Sample_Period

    import os
    os.makedirs(CSV_Output_dir, exist_ok=True)

    csv_path = f"{CSV_Output_dir}/{name}.csv"
    err_path = f"{CSV_Output_dir}/{name}_errors.log"

    with open(err_path, "a", encoding="utf-8") as err_f:
        _log_err(err_f, "START unified logger")
        _log_err(err_f, f"CONFIG  duration_s={duration_s} Sampling_Period={Sampling_Period} Min_Sample_Period={Min_Sample_Period}")
        _log_err(err_f, f"CONFIG  DAQ1=0x{DAQ1_I2C_ADDR:02X} DAQ2=0x{DAQ2_I2C_ADDR:02X} ADC=0x{ADC_ADDR:02X}")
        _log_err(err_f, f"CONFIG  ADC_Channel={ADC_Channel} ADC_Gain={ADC_Gain}")

        dev1, dev2, ads = Check_Device_connection(err_f)
        headers = Set_Headers()

        start = time.monotonic()
        end = start + float(duration_s)
        idx = 0

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

            while time.monotonic() < end:
                loop_start = time.monotonic()
                idx += 1

                row_base = {
                    "index": idx,
                    "timestamp": _timestamp_ms(),
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

                try:
                    raw1 = dev1.get_information(dev1.eALL, True)
                    parsed1 = _parse_daq1_eall(raw1, err_f)

                    t_clean, v_p2_temp = Validate_Value(parsed1.get("p2.Temp_Air"), min_v=-30.0, max_v=80.0)
                    rh_clean, v_p2_rh = Validate_Value(parsed1.get("p2.Humi_Air"), min_v=0.0, max_v=100.0)
                    co2_clean, v_p3_co2 = Validate_Value(parsed1.get("p3.CO2"), min_v=0.0, max_v=100000.0)

                    daq1_vals = {"p2.Temp_Air": t_clean, "p2.Humi_Air": rh_clean, "p3.CO2": co2_clean}
                    if v_p2_temp or v_p2_rh or v_p3_co2:
                        row_base["DAQ1_ok"] = 1
                except Exception as e:
                    _log_err(err_f, f"DAQ1  exception  {repr(e)}")

                # -------- DAQ2 --------
                daq2_vals = {"d2.NH3": "", "d2.H2S": ""}
                v_d2_nh3 = 0
                v_d2_h2s = 0

                try:
                    nh3, h2s, _raw2 = _read_daq2(dev2, err_f)
                    nh3_clean, v_d2_nh3 = Validate_Value(nh3, min_v=0.0, max_v=10000.0)
                    h2s_clean, v_d2_h2s = Validate_Value(h2s, min_v=0.0, max_v=10000.0)
                    daq2_vals = {"d2.NH3": nh3_clean, "d2.H2S": h2s_clean}
                    if v_d2_nh3 or v_d2_h2s:
                        row_base["DAQ2_ok"] = 1
                except Exception as e:
                    _log_err(err_f, f"DAQ2  exception  {repr(e)}")

                # ADC (Methane
                ch4_vout, v_ch4 = Read_ADC_Methane(ads, ADC_Channel, ADC_Gain, err_f)
                if v_ch4:
                    row_base["ADC_ok"] = 1

                validity = {
                    "valid_p2_temp": v_p2_temp,
                    "valid_p2_rh": v_p2_rh,
                    "valid_p3_co2": v_p3_co2,
                    "valid_d2_nh3": v_d2_nh3,
                    "valid_d2_h2s": v_d2_h2s,
                    "valid_ch4_vout": v_ch4,
                }

                row = Merge_row_dicts(
                    row_base,
                    daq1_vals,
                    daq2_vals,
                    {"CH4_Vout": ch4_vout},
                    validity
                )

                elapsed = time.monotonic() - loop_start
                if elapsed > Sampling_Period:
                    row["overrun"] = 1
                    _log_err(err_f, f"Time_Out_Err | overrun | elapsed={elapsed:.3f}s period={Sampling_Period:.3f}s")

                writer.writerow(row)
                f.flush()

                sleep_for = Sampling_Period - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)

        _log_err(err_f, f"STOP | rows={idx} csv='{csv_path}'")

    return csv_path

def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--name", "-n", required=True)
    p.add_argument("--duration", "-d", type=float, required=True)
    p.add_argument("--outdir", "-o", default="out")
    p.add_argument("--period", "-p", type=float, default=5.0)
    p.add_argument("--min-period", type=float, default=5.0)
    p.add_argument("--adc-channel", type=int, default=0)
    p.add_argument("--adc-gain", type=float, default=1)
    return p.parse_args()


def main():
    args = _parse_args()
    run_logger(
        name=args.name,
        duration_s=args.duration,
        CSV_Output_dir=args.outdir,
        Sampling_Period=args.period,
        Min_Sample_Period=args.min_period,
        ADC_Channel=args.adc_channel,
        ADC_Gain=args.adc_gain
    )


if __name__ == "__main__":
    main()



    """
########################################################
    Add this to your script at the top helper functions: 
########################################################


    from datetime import datetime
from your_logger_file import run_logger


# create one fixed timestamp for the whole run
run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")

# starting position in the run
bed_num = 1
point_num = 1


def build_sample_name(bed_num, point_num, run_timestamp):
    return f"BED{bed_num}_P{point_num}_{run_timestamp}"


def increment_bed_point(bed_num, point_num):
    if point_num < 6:
        return bed_num, point_num + 1
    return bed_num + 1, 1



###########################################################
each time you sample a location so the below 
###########################################################

csv_name = build_sample_name(bed_num, point_num, run_timestamp)

run_logger(
    name=csv_name,
    duration_s=30,
    CSV_Output_dir="out",
    Sampling_Period=5.0,
    Min_Sample_Period=5.0,
    ADC_Channel=0,
    ADC_Gain=1
)

bed_num, point_num = increment_bed_point(bed_num, point_num)

    """