#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""

  @file Extract_Files.py
  @brief 
  @author Brandon-lee Craddock
  @maintainer Jade Cawley
  @version  V1.0
  @data 2026-03-03

Cubiclean session extraction and visual data builder

Main program flow

1. Scan the CSV output directory and identify files that match the expected
   naming format for bed, point, and timestamp.
2. Group matching CSV files into bed sessions using:
   Bed_ID + TimeStamp -> one session key.
3. For each session:
   - sort the point CSVs
   - detect missing or duplicate points
   - mark whether the session is complete
4. Load each point CSV and convert its sensor columns into time-series data.
5. Interpolate short gaps in the sensor readings and compare values against
   baseline thresholds.
6. Build sensor-level summaries for each point, then classify each point into
   a colour status.
7. Combine point-level results into a bed-level summary and classify the whole
   bed session.
8. Build final output structures used by the Dash app:
   - All_sessions_map
   - Session_overview
   - Still_logging_session
"""

import os
import re
import csv


def Extract_filename(file_name):
    """Extract bed ID, point ID, and timestamp from a CSV filename."""

    m = re.match(r"^(BED\d+)_P([1-6])_(\d{4}-\d{2}-\d{2}_\d{4})\.csv$", file_name)
    if not m:
        return None
    return {
        "Bed_ID": m.group(1),
        "Point_ID": int(m.group(2)),
        "TimeStamp": m.group(3),
        "CSV_Path": file_name,
    }


def idx_sample_csvs(CSV_Output_dir):
    """
    Scan the CSV output directory and return data for all valid sample csvs.
    only files matching the expected filename pattern are included.
    """
    rows = []
    if not os.path.isdir(CSV_Output_dir):
        return rows

    for fn in os.listdir(CSV_Output_dir):
        if not fn.lower().endswith(".csv"):
            continue
        parsed = Extract_filename(fn)
        if parsed is None:
            continue
        parsed["CSV_Path"] = os.path.join(CSV_Output_dir, fn)
        rows.append(parsed)

    return rows


def Sort_Bed_Samples(samples):
    """
    Sort a bed session's point samples by point ID and detect
    - missing points
    - duplicate points
    """
    sorted_samples = sorted(samples, key=lambda x: int(x["Point_ID"]))

    seen = {}
    duplicate_points = []
    for s in sorted_samples:
        pid = int(s["Point_ID"])
        if pid in seen:
            duplicate_points.append(pid)
        seen[pid] = True

    missing_points = [p for p in range(1, 7) if p not in seen]
    return sorted_samples, missing_points, duplicate_points


def Group_data_by_bed(rows):

    """
    Group parsed CSV file rows into sessions using
    Bed_ID + TimeStamp -> Session_Key

    each grouped session is checked for missing or duplicate points and marked
    as complete only if it contains exactly one csv for each point 1 to 6.
    """

    grouped = {}

    for row in rows:
        key = f"{row['Bed_ID']}__{row['TimeStamp']}"
        if key not in grouped:
            grouped[key] = {
                "Session_Key": key,
                "Bed_ID": row["Bed_ID"],
                "TimeStamp": row["TimeStamp"],
                "Samples": [],
            }
        grouped[key]["Samples"].append(row)

    out = {}
    for key, session in grouped.items():
        sorted_samples, missing_points, duplicate_points = Sort_Bed_Samples(session["Samples"])

        out[key] = {
            "Session_Key": key,
            "Bed_ID": session["Bed_ID"],
            "TimeStamp": session["TimeStamp"],
            "Samples": sorted_samples,
            "Missing_Points": missing_points,
            "Duplicate_Points": duplicate_points,
            "Complete": 1 if (len(missing_points) == 0 and len(duplicate_points) == 0 and len(sorted_samples) == 6) else 0,
        }

    return out


def Load_Sample_CSV(CSV_Path, Sampling_Period=5.0):

    """
    Load a single point csv and convert it into time-series channel data.

    time is reconstructed using the sampling period rather than read directly
    from the csv.
    """

    time_s = []

    Temp_Air = []
    Humi_Air = []
    CO2_ppm = []
    NH3_ppm = []
    H2S_ppm = []
    CH4_Vout = []

    def _to_float(v):
        try:
            if v is None:
                return None
            s = str(v).strip()
            if s == "":
                return None
            return float(s)
        except Exception:
            return None

    with open(CSV_Path, "r", newline="") as f:
        reader = csv.DictReader(f)

        i = 0
        for row in reader:
            time_s.append(i * float(Sampling_Period))
            i += 1

            
            Temp_Air.append(_to_float(row.get("p2.Temp_Air")))
            Humi_Air.append(_to_float(row.get("p2.Humi_Air")))

            
            CO2_ppm.append(_to_float(
                row.get("p2.CO2_ppm") if row.get("p2.CO2_ppm") is not None else row.get("p3.CO2")
            ))

            
            NH3_ppm.append(_to_float(
                row.get("p1.NH3_ppm") if row.get("p1.NH3_ppm") is not None else row.get("d2.NH3")
            ))
            H2S_ppm.append(_to_float(
                row.get("p1.H2S_ppm") if row.get("p1.H2S_ppm") is not None else row.get("d2.H2S")
            ))

            
            CH4_Vout.append(_to_float(
                row.get("p3.CH4_Vout") if row.get("p3.CH4_Vout") is not None else row.get("CH4_Vout")
            ))

           

    channels = {
        "Temp_Air": Temp_Air,
        "Humi_Air": Humi_Air,
        "CO2_ppm": CO2_ppm,
        "NH3_ppm": NH3_ppm,
        "H2S_ppm": H2S_ppm,
        "CH4_Vout": CH4_Vout,
    }
    # Build a matching valid flag array for each channel so later stages can
    # distinguish real readings from missing data.
    valid_flags = {}
    for k, arr in channels.items():
        flags = []
        for v in arr:
            flags.append(1 if v is not None else 0)
        valid_flags[k] = flags

    return {
        "CSV_Path": CSV_Path,
        "Sampling_Period": float(Sampling_Period),
        "time_s": time_s,
        "channels": channels,
        "valid_flags": valid_flags,
        "n_rows": len(time_s),
    }


def Build_Bed_data(Session, Sampling_Period=5.0):
    """
    Load all point csvs for a single session and combine them into one bed data
    structure keyed by point ID.
    """
    points = {}

    for sample in Session.get("Samples", []):
        pid = int(sample["Point_ID"])

        if pid not in points:
            points[pid] = Load_Sample_CSV(sample["CSV_Path"], Sampling_Period=Sampling_Period)

    return {
        "Bed_ID": Session.get("Bed_ID"),
        "TimeStamp": Session.get("TimeStamp"),
        "Complete": int(Session.get("Complete", 0)),
        "Missing_Points": list(Session.get("Missing_Points", [])),
        "Duplicate_Points": list(Session.get("Duplicate_Points", [])),
        "Points": points,
    }


def Interpolate_short_gaps(values, valid_flags, max_gap=1):
    """
    Fill short runs of missing samples by linear interpolation when
    - the gap length is within max_gap
    - valid samples exist on both sides of the gap
    """
    n = len(values)
    if n == 0:
        return [], []

    out = list(values)
    out_valid = list(valid_flags)

    i = 0
    while i < n:
        if int(out_valid[i]) == 1:
            i += 1
            continue

        gap_start = i
        while i < n and int(out_valid[i]) == 0:
            i += 1
        gap_end = i - 1
        gap_len = gap_end - gap_start + 1

        if gap_len > int(max_gap):
            continue

        left_i = gap_start - 1
        right_i = gap_end + 1

        if left_i < 0 or right_i >= n:
            continue

        if int(out_valid[left_i]) != 1 or int(out_valid[right_i]) != 1:
            continue

        left_v = out[left_i]
        right_v = out[right_i]
        if left_v is None or right_v is None:
            continue

        step = (right_v - left_v) / float(gap_len + 1)
        for k in range(gap_len):
            idx = gap_start + k
            out[idx] = left_v + step * (k + 1)
            out_valid[idx] = 1

    return out, out_valid


def Reading_spikes(Point_Data, Baseline_thresholds, Interp_Max_Gap=1):
    """
    Process one point's sensor channels by
    - interpolating short gaps
    - checking whether each value is inside the threshold range
    - marking values above the upper threshold
    - calculating simple gradients
    """
    time_s = list(Point_Data.get("time_s", []))
    raw_channels = Point_Data.get("channels", {})
    raw_valid_flags = Point_Data.get("valid_flags", {})

    out_channels = {}

    for sensor_name, values in raw_channels.items():
        valid_flags = list(raw_valid_flags.get(sensor_name, [0] * len(values)))

        interp_values, interp_valid = Interpolate_short_gaps(
            values,
            valid_flags,
            max_gap=Interp_Max_Gap
        )

        sensor_thresh = Baseline_thresholds.get(sensor_name, {})
        vmin = sensor_thresh.get("Min", None)
        vmax = sensor_thresh.get("Max", None)

        baseline_flags = []
        above_baseline = []

        for i, v in enumerate(interp_values):
            is_valid = 1 if i < len(interp_valid) and int(interp_valid[i]) == 1 and v is not None else 0
            if is_valid == 0:
                baseline_flags.append(0)
                above_baseline.append(0)
                continue

            in_range = 1
            if vmin is not None and v < vmin:
                in_range = 0
            if vmax is not None and v > vmax:
                in_range = 0

            baseline_flags.append(in_range)

            if vmax is None:
                above_baseline.append(0)
            else:
                above_baseline.append(1 if v > vmax else 0)
        # Calculate a simple per-sample gradient using the sampling period.
        gradients = [None]
        for i in range(1, len(interp_values)):
            v0 = interp_values[i - 1]
            v1 = interp_values[i]
            ok0 = int(interp_valid[i - 1]) == 1 if i - 1 < len(interp_valid) else False
            ok1 = int(interp_valid[i]) == 1 if i < len(interp_valid) else False

            if (not ok0) or (not ok1) or (v0 is None) or (v1 is None):
                gradients.append(None)
            else:
                dt = float(Point_Data.get("Sampling_Period", 1.0))
                if dt == 0:
                    gradients.append(None)
                else:
                    gradients.append((v1 - v0) / dt)

        out_channels[sensor_name] = {
            "raw_values": list(values),
            "raw_valid": list(valid_flags),
            "interp_values": interp_values,
            "interp_valid": interp_valid,
            "baseline_flags": baseline_flags,
            "above_baseline": above_baseline,
            "gradients": gradients,
        }

    return {
        "time_s": time_s,
        "channels": out_channels,
    }


def Sum_point_sensor_data(time_s, Sensor_Channel_Data, Point_classify_params):

    """
    Build a sensor-level summary for one point channel.

    This calculates the main statistics and assigns a sensor state such as
    - NO_DATA 
    - LOW_VALID  
    - BASELINE 
    - TRANSIENT_RISE 
    - SETTLED_SPIKE 
    """

    interp_values = list(Sensor_Channel_Data.get("interp_values", []))
    interp_valid = list(Sensor_Channel_Data.get("interp_valid", []))
    above_baseline = list(Sensor_Channel_Data.get("above_baseline", []))
    gradients = list(Sensor_Channel_Data.get("gradients", []))

    n_total = len(interp_values)
    n_valid = sum(1 for f in interp_valid if int(f) == 1)

    Min_valid_count = int(Point_classify_params.get("Min_valid_count", 3))
    Min_valid_check = float(Point_classify_params.get("Min_valid_check", 0.5))
    Num_above_min = int(Point_classify_params.get("Num_above_min", 1))
    Gradient_Thresh = float(Point_classify_params.get("Gradient_Thresh", 0.01))
    Plateau_thresh = float(Point_classify_params.get("Plateau_thresh", 0.005))
    Settled_tail_check = float(Point_classify_params.get("Settled_tail_check", 0.02))
    Consecutive_Above_thresh = int(Point_classify_params.get("Consecutive_Above_thresh", 2))
    Tails_window_len = int(Point_classify_params.get("Tails_window_len", 3))

    valid_ratio = (float(n_valid) / float(n_total)) if n_total > 0 else 0.0

    usable = 1
    if n_valid < Min_valid_count:
        usable = 0
    if valid_ratio < Min_valid_check:
        usable = 0

    values_valid_only = []
    for i, v in enumerate(interp_values):
        if i < len(interp_valid) and int(interp_valid[i]) == 1 and v is not None:
            values_valid_only.append(v)

    if len(values_valid_only) == 0:
        return {
            "Usable": 0,
            "n_total": n_total,
            "n_valid": n_valid,
            "valid_ratio": valid_ratio,
            "n_above": 0,
            "n_consecutive_above_max": 0,
            "max_value": None,
            "min_value": None,
            "mean_value": None,
            "tail_mean": None,
            "tail_grad_mean_abs": None,
            "Sens_state": "NO_DATA",
        }

    max_value = max(values_valid_only)
    min_value = min(values_valid_only)
    mean_value = sum(values_valid_only) / float(len(values_valid_only))

    n_above = sum(1 for x in above_baseline if int(x) == 1)

    # Find the longest consecutive run of above-threshold samples.
    max_consec = 0
    curr = 0
    for x in above_baseline:
        if int(x) == 1:
            curr += 1
            if curr > max_consec:
                max_consec = curr
        else:
            curr = 0

    tail_values = []
    tail_grad_abs = []

    # Use the tail of the signal to help decide whether the response is
    # settled or transient.

    i0 = max(0, len(interp_values) - Tails_window_len)
    for i in range(i0, len(interp_values)):
        if i < len(interp_valid) and int(interp_valid[i]) == 1 and interp_values[i] is not None:
            tail_values.append(interp_values[i])

        if i < len(gradients):
            g = gradients[i]
            if g is not None:
                tail_grad_abs.append(abs(float(g)))

    tail_mean = (sum(tail_values) / float(len(tail_values))) if len(tail_values) > 0 else None
    tail_grad_mean_abs = (sum(tail_grad_abs) / float(len(tail_grad_abs))) if len(tail_grad_abs) > 0 else None

    if usable == 0:
        sens_state = "LOW_VALID"
    else:
        settled_like = 0
        transient_like = 0

        if n_above >= Num_above_min:
            transient_like = 1

        if max_consec >= Consecutive_Above_thresh:
            transient_like = 1

        if tail_grad_mean_abs is not None and tail_grad_mean_abs <= Plateau_thresh and n_above >= 1:
            settled_like = 1

        if tail_grad_mean_abs is not None and tail_grad_mean_abs <= Settled_tail_check and n_above >= 1:
            settled_like = 1

        if tail_grad_mean_abs is not None and tail_grad_mean_abs >= Gradient_Thresh and n_above >= 1:
            transient_like = 1

        if settled_like == 1:
            sens_state = "SETTLED_SPIKE"
        elif transient_like == 1:
            sens_state = "TRANSIENT_RISE"
        else:
            sens_state = "BASELINE"

    return {
        "Usable": usable,
        "n_total": n_total,
        "n_valid": n_valid,
        "valid_ratio": valid_ratio,
        "n_above": n_above,
        "n_consecutive_above_max": max_consec,
        "max_value": max_value,
        "min_value": min_value,
        "mean_value": mean_value,
        "tail_mean": tail_mean,
        "tail_grad_mean_abs": tail_grad_mean_abs,
        "Sens_state": sens_state,
    }


def Set_point_status(Point_Sensor_Summaries):
    """
    Convert the set of sensor states for one point into a single point colour.
    """

    if not Point_Sensor_Summaries:
        return "grey"

    n_usable = 0
    n_settled = 0
    n_transient = 0

    key_gas = ["NH3_ppm", "H2S_ppm", "CH4_Vout", "CO2_ppm"]
    key_states = []

    for sensor_name, s in Point_Sensor_Summaries.items():
        state = str(s.get("Sens_state", "NO_DATA")).upper()
        usable = int(s.get("Usable", 0))

        if usable == 1:
            n_usable += 1

        if state == "SETTLED_SPIKE":
            n_settled += 1
        elif state == "TRANSIENT_RISE":
            n_transient += 1

        # Give extra weighting to the main gas channels used in point grading.
        if sensor_name in key_gas:
            key_states.append(state)

    if n_usable == 0:
        return "grey"

    n_key_settled = sum(1 for st in key_states if st == "SETTLED_SPIKE")
    n_key_transient = sum(1 for st in key_states if st == "TRANSIENT_RISE")

    if (n_key_settled >= 2) or ((n_key_settled >= 1) and (n_key_transient >= 1)) or (n_settled >= 3):
        return "red"

    if (n_settled >= 1) or (n_transient >= 1):
        return "amber"

    return "green"


def Build_sum_for_each_point(Point_Data, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):

    """
    Build the full processed output for one point including
    - processed sensor traces
    - sensor summaries
    - final point colour grading
    """

    Reading_spikes_out = Reading_spikes(
        Point_Data,
        Baseline_thresholds,
        Interp_Max_Gap=Interp_Max_Gap
    )

    Point_sensor_summaries = {}
    for sensor_name, sensor_channel_data in Reading_spikes_out["channels"].items():
        Point_sensor_summaries[sensor_name] = Sum_point_sensor_data(
            Reading_spikes_out["time_s"],
            sensor_channel_data,
            Point_classify_params
        )

    Point_colour_grading = Set_point_status(Point_sensor_summaries)

    return {
        "time_s": Reading_spikes_out["time_s"],
        "Point_sensor_summaries": Point_sensor_summaries,
        "Point_colour_grading": Point_colour_grading,
        "Reading_spikes_out": Reading_spikes_out,
    }


def Set_Bed_status(Bed_Point_Summaries):
    """
    Convert the set of point colours for one bed session into a single bed colour.
    """
    if not Bed_Point_Summaries:
        return "grey"

    point_colours = []
    for pid, p in Bed_Point_Summaries.items():
        point_colours.append(str(p.get("Point_colour_grading", "grey")).lower())

    n_red = sum(1 for c in point_colours if c == "red")
    n_amber = sum(1 for c in point_colours if c == "amber")
    n_grey = sum(1 for c in point_colours if c == "grey")

    if n_red >= 1:
        return "red"

    if n_amber >= 1:
        return "amber"

    if n_grey == len(point_colours):
        return "grey"

    return "green"


def Build_Bed_Visual_data(Bed_Data, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):
    """
    Build the final visual data structure for one bed session.

    This combines all point-level outputs and adds the overall bed summary
    used by the Dash app.
    """
    Bed_point_sumup = {}
    Point_colour_map = {}

    point_ids = sorted(Bed_Data.get("Points", {}).keys())

    for pid in point_ids:
        point_data = Bed_Data["Points"][pid]

        point_out = Build_sum_for_each_point(
            point_data,
            Baseline_thresholds,
            Point_classify_params,
            Interp_Max_Gap=Interp_Max_Gap
        )

        Bed_point_sumup[pid] = point_out
        Point_colour_map[pid] = point_out.get("Point_colour_grading", "grey")

    Bed_colour_grading = Set_Bed_status(Bed_point_sumup)

    colours = [str(c).lower() for c in Point_colour_map.values()]
    n_green = sum(1 for c in colours if c == "green")
    n_amber = sum(1 for c in colours if c == "amber")
    n_red = sum(1 for c in colours if c == "red")
    n_grey = sum(1 for c in colours if c == "grey")

    Bed_status_summary = {
        "n_points_present": len(point_ids),
        "n_points_expected": 6,
        "n_green": n_green,
        "n_amber": n_amber,
        "n_red": n_red,
        "n_grey": n_grey,
        "is_complete_session": 1 if int(Bed_Data.get("Complete", 0)) == 1 else 0
    }

    return {
        "Bed_ID": Bed_Data.get("Bed_ID"),
        "TimeStamp": Bed_Data.get("TimeStamp"),
        "Complete": Bed_Data.get("Complete", 0),
        "Missing_Points": list(Bed_Data.get("Missing_Points", [])),
        "Duplicate_Points": list(Bed_Data.get("Duplicate_Points", [])),
        "Bed_point_sumup": Bed_point_sumup,
        "Point_colour_map": Point_colour_map,
        "Bed_colour_grading": Bed_colour_grading,
        "Bed_status_summary": Bed_status_summary,
    }


def Build_session_overview(Session_Key, bed_visual):
    """
    Build a compact summary row for one session to support overview displays.
    """
    bed_status_summary = bed_visual.get("Bed_status_summary", {})
    return {
        "Session_Key": Session_Key,
        "Bed_ID": bed_visual.get("Bed_ID"),
        "TimeStamp": bed_visual.get("TimeStamp"),
        "Complete": int(bed_visual.get("Complete", 0)),
        "Bed_colour_grading": bed_visual.get("Bed_colour_grading", "grey"),
        "n_points_present": int(bed_status_summary.get("n_points_present", 0)),
        "n_points_expected": int(bed_status_summary.get("n_points_expected", 6)),
        "Missing_Points": list(bed_visual.get("Missing_Points", [])),
        "Duplicate_Points": list(bed_visual.get("Duplicate_Points", [])),
    }


def Detect_still_logging_sessions(All_sessions_map):
    """
    Return the list of sessions that are not yet complete.
    """
    Still_logging_session = []
    for Session_Key in sorted(All_sessions_map.keys()):
        bed_visual = All_sessions_map[Session_Key]
        if int(bed_visual.get("Complete", 0)) == 0:
            Still_logging_session.append(Session_Key)
    return Still_logging_session


def Build_All_sessions_map(sessions, Sampling_Period, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):
    """
    Build the full visual data map for all grouped sessions.

    """
    All_sessions_map = {}
    for Session_Key in sorted(sessions.keys()):
        Session = sessions[Session_Key]
        Bed_Data = Build_Bed_data(Session, Sampling_Period=Sampling_Period)
        bed_visual = Build_Bed_Visual_data(
            Bed_Data,
            Baseline_thresholds,
            Point_classify_params,
            Interp_Max_Gap=Interp_Max_Gap
        )
        All_sessions_map[Session_Key] = bed_visual
    return All_sessions_map


def Build_All_session_visual_data(CSV_Output_dir, Sampling_Period, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):
    """
    Main extraction pipeline for the session visualisation data.

    This is the main entry point used by the Dash app.
    """
    rows = idx_sample_csvs(CSV_Output_dir)
    sessions = Group_data_by_bed(rows)

    All_sessions_map = Build_All_sessions_map(
        sessions=sessions,
        Sampling_Period=Sampling_Period,
        Baseline_thresholds=Baseline_thresholds,
        Point_classify_params=Point_classify_params,
        Interp_Max_Gap=Interp_Max_Gap
    )

    Session_overview = []
    for Session_Key in sorted(All_sessions_map.keys()):
        Session_overview.append(Build_session_overview(Session_Key, All_sessions_map[Session_Key]))

    Still_logging_session = Detect_still_logging_sessions(All_sessions_map)

    return {
        "All_sessions_map": All_sessions_map,
        "Session_overview": Session_overview,
        "Still_logging_session": Still_logging_session,
    }


def Refresh_All_session_visual_data(CSV_Output_dir, Sampling_Period, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):
    """
    Rebuild all session visual data from the current csv directory contents.
    """
    return Build_All_session_visual_data(
        CSV_Output_dir=CSV_Output_dir,
        Sampling_Period=Sampling_Period,
        Baseline_thresholds=Baseline_thresholds,
        Point_classify_params=Point_classify_params,
        Interp_Max_Gap=Interp_Max_Gap
    )


def Refresh_session_visual_data(CSV_Output_dir, Sampling_Period, Baseline_thresholds, Point_classify_params, Interp_Max_Gap=1):
    """
    Wrapper kept for compatibility with earlier naming.
    """
    return Refresh_All_session_visual_data(
        CSV_Output_dir=CSV_Output_dir,
        Sampling_Period=Sampling_Period,
        Baseline_thresholds=Baseline_thresholds,
        Point_classify_params=Point_classify_params,
        Interp_Max_Gap=Interp_Max_Gap
    )


if __name__ == "__main__":
    TEST_DIR = r"C:\Users\brand\source\repos\out_mock"

    Baseline_thresholds_classify = {
        "Temp_Air": {"Min": -10.0, "Max": 45.0},
        "Humi_Air": {"Min": 0.0, "Max": 100.0},
        "CO2_ppm": {"Min": 300.0, "Max": 1500.0},
        "NH3_ppm": {"Min": 0.0, "Max": 15.0},
        "H2S_ppm": {"Min": 0.0, "Max": 5.0},
        "CH4_Vout": {"Min": 0.0, "Max": 1.8},
    }

    Point_classify_params = {
        "Tails_window_len": 3,
        "Min_valid_count": 3,
        "Min_valid_check": 0.5,
        "Num_above_min": 1,
        "Baseline_buffer": 0.0,
        "Gradient_Thresh": 0.01,
        "Plateau_thresh": 0.005,
        "Settled_tail_check": 0.02,
        "Consecutive_Above_thresh": 2,
    }

    out = Build_All_session_visual_data(
        CSV_Output_dir=TEST_DIR,
        Sampling_Period=5.0,
        Baseline_thresholds=Baseline_thresholds_classify,
        Point_classify_params=Point_classify_params,
        Interp_Max_Gap=1
    )

    print("Sessions:", len(out["All_sessions_map"]))
    print("Still logging:", out["Still_logging_session"])
    for row in out["Session_overview"]:
        print(row["Session_Key"], row["Bed_colour_grading"], row["n_points_present"], "/", row["n_points_expected"])