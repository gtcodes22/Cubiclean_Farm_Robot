#!/usr/bin/env python3
# -*- coding:utf-8 -*-


"""
Cubiclean Bed Viewer

Main program flow

1. Load and process all CSV session data using Build_All_session_visual_data().
2. Build session/date/run lookup data for the dropdowns and determine the default selections, usually from the most recent available run.
3. Create the initial app state used to track the current view and selections. This is stored in a dcc.Store
and updated via callbacks whenever the user clicks or changes controls. The app state includes:
    - Current_view: overview, bed, point, single_sensor_full, or day_progression
    - Selected_session_key: the unique key for the selected session/bed
    - Selected_point_id: the currently selected point (1-6) when in point or single_sensor_full view
    - Selected_sensor_name: the currently selected sensor name when in single_sensor_full view
    - Nav_history: a list of previous app states to support back navigation

4. Build the Dash layout:
   - top controls for date, session and beds/page selection
   - navigation buttons for home, back, page navigation, and day progression
   - main content area that conditionally renders based on the current view in the app state
   - graph area
   - sensor stats area that shows stats for the currently selected sensor when in single_sensor_full view

5. Periodically refresh the processed data so new/updated runs can appear.

6. Use one callback to update the stored app state whenever the user clicks or changes controls.

7. Use one render callback to turn the stored app state into visible page content.
    This callback reads the current view and selections from the app state and calls helper functions to build the appropriate content for that view.

8. Support drill-down navigation:
   Overview -> Bed -> Point -> Single sensor full view
   plus day progression and back/home navigation.

"""


import os
import json
import statistics
from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL, no_update

from Extract_Files import Build_All_session_visual_data

#Display labels used for sensor plot y-axes and the sensor stats panel.
SENSOR_LABELS = {
    "Temp_Air": "Temp (°C)",
    "Humi_Air": "RH (%)",
    "CO2_ppm": "CO₂ (ppm)",
    "NH3_ppm": "NH₃ (ppm)",
    "H2S_ppm": "H₂S (ppm)",
    "CH4_Vout": "CH₄ Vout (V)",
}

# helper functions
###############################################################

def _safe_int(value, default=0):

    """Safely convert a value to an integer returning a default if conversion fails."""

    try:
        return int(value)
    except Exception:
        return default


def _safe_float(value, default=None):

    """Safely convert a value to a float returning a default if conversion fails."""

    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _rect_poly_xy(x0, y0, x1, y1):

    """Return the x and y coordinates for a rectangle polygon defined by the corners (x0, y0) and (x1, y1)."""

    return [x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0]


def _split_session_key(Session_Key):

    """Split a session key of the format 'BedID__TimeStamp' into its components."""

    if not isinstance(Session_Key, str):
        return {"Bed_ID": None, "TimeStamp": None}
    if "__" in Session_Key:
        Bed_ID, TimeStamp = Session_Key.split("__", 1)
        return {"Bed_ID": Bed_ID, "TimeStamp": TimeStamp}
    return {"Bed_ID": None, "TimeStamp": None}


def _extract_session_date(TimeStamp):

    """Extract the date portion from a timestamp string in the form 'YYYY-MM-DD...'."""

    if not isinstance(TimeStamp, str):
        return None
    return TimeStamp[:10] if len(TimeStamp) >= 10 else None


def _extract_run_label(TimeStamp):

    """Extract a run label from the timestamp which is the part after the first underscore."""

    if not isinstance(TimeStamp, str):
        return ""
    parts = TimeStamp.split("_")
    if len(parts) >= 2:
        return parts[1]
    return TimeStamp


def _bed_sort_key_from_session_key(Session_Key):

    """Extract a sort key from the session key that sorts by bed number if possible, otherwise puts it at the end."""

    parts = _split_session_key(Session_Key)
    bed_id = str(parts.get("Bed_ID") or "")
    digits = "".join([c for c in bed_id if c.isdigit()])
    if digits != "":
        return (0, int(digits), bed_id)
    return (1, 999999, bed_id)


def _status_class_from_colour(colour_name: str):
    """Convert a colour name to a CSS class for status indication."""
    c = str(colour_name or "grey").lower()
    if c == "green":
        return "status-good"
    if c == "amber":
        return "status-warn"
    if c == "red":
        return "status-bad"
    return "status-off"


def _get_triggered_id():
    """
    Return the ID of the input that triggered the current callback.

    This supports both normal Dash component IDs and pattern-matching IDs.
    """
    try:
        trig = callback_context.triggered_id
        if trig is not None:
            return trig
    except Exception:
        pass

    try:
        prop_id = callback_context.triggered[0]["prop_id"].split(".")[0]
    except Exception:
        return None

    if prop_id.startswith("{"):
        try:
            return json.loads(prop_id)
        except Exception:
            return prop_id
    return prop_id


def _pattern_click_count(triggered_id):
    """
    For a pattern-matching component, return the n_clicks value that belongs
    to the triggered component.

    This is used to ignore components that have merely been rendered but not
    actually clicked by the user.
    """
    if not isinstance(triggered_id, dict):
        return 0

    try:
        inputs_grouped = callback_context.inputs_list
    except Exception:
        return 0

    if not isinstance(inputs_grouped, list):
        return 0

    for group in inputs_grouped:
        if not isinstance(group, list):
            continue
        for item in group:
            if not isinstance(item, dict):
                continue
            if item.get("id") == triggered_id:
                return _safe_int(item.get("value"), 0)

    return 0


###############################################################

def Build_session_run_map(All_sessions_map):
    """
    Group all session keys by run timestamp and by date.

    Output is used to:
    - populate the session dropdown
    - filter runs by selected date
    - find which bed session keys belong to a selected run
    """
    Session_run_map = {}
    Runs_by_date = {}

    if not isinstance(All_sessions_map, dict):
        return {"Session_run_map": {}, "Runs_by_date": {}, "All_run_keys": []}

    for Session_Key in sorted(All_sessions_map.keys()):
        bed_vis = All_sessions_map[Session_Key]
        TimeStamp = str(bed_vis.get("TimeStamp", ""))
        Date_Key = _extract_session_date(TimeStamp)
        if TimeStamp == "":
            continue

        Session_run_map.setdefault(TimeStamp, {"Run_TimeStamp": TimeStamp, "Run_Date": Date_Key, "Bed_keys": []})
        Session_run_map[TimeStamp]["Bed_keys"].append(Session_Key)

        if Date_Key is not None:
            Runs_by_date.setdefault(Date_Key, [])
            if TimeStamp not in Runs_by_date[Date_Key]:
                Runs_by_date[Date_Key].append(TimeStamp)

    for Run_TimeStamp in Session_run_map.keys():
        Session_run_map[Run_TimeStamp]["Bed_keys"] = sorted(
            Session_run_map[Run_TimeStamp]["Bed_keys"],
            key=_bed_sort_key_from_session_key
        )

    for Date_Key in Runs_by_date.keys():
        Runs_by_date[Date_Key] = sorted(Runs_by_date[Date_Key])

    All_run_keys = sorted(Session_run_map.keys())
    return {"Session_run_map": Session_run_map, "Runs_by_date": Runs_by_date, "All_run_keys": All_run_keys}


def Filter_runs_by_date(Session_selector_data, Selected_session_date):

    """Given the session selector data and a selected date return the list of run keys that correspond to that date."""

    Runs_by_date = Session_selector_data.get("Runs_by_date", {})
    if not Selected_session_date:
        return []
    return list(Runs_by_date.get(Selected_session_date, []))


def Pull_run_bed_keys(Session_selector_data, Selected_session_run_key):
    """Given the session selector data and a selected run key return the list of bed session keys that correspond to that run."""

    Session_run_map = Session_selector_data.get("Session_run_map", {})
    run_row = Session_run_map.get(Selected_session_run_key, {})
    return list(run_row.get("Bed_keys", []))


def Build_run_options(Run_keys_on_date, Session_selector_data, All_sessions_map):

    """
    Build the visible dropdown labels for the selected day's runs.

    Each option includes:
    - run label
    - number of beds
    - count of beds by status colour

    """


    Session_run_map = Session_selector_data.get("Session_run_map", {})
    opts = []
    #  Build a dropdown option for each run available on the selected date.
    for Run_Key in Run_keys_on_date:
        run_row = Session_run_map.get(Run_Key, {})
        bed_keys = list(run_row.get("Bed_keys", []))

        n_beds = len(bed_keys)
        n_red = n_amber = n_green = n_grey = 0
        for sk in bed_keys:
            bed_vis = All_sessions_map.get(sk, {})
            c = str(bed_vis.get("Bed_colour_grading", "grey")).lower()
            if c == "red":
                n_red += 1
            elif c == "amber":
                n_amber += 1
            elif c == "green":
                n_green += 1
            else:
                n_grey += 1

        label = f"{_extract_run_label(Run_Key)} | beds:{n_beds} | R:{n_red} A:{n_amber} G:{n_green} Grey:{n_grey}"
        opts.append({"label": label, "value": Run_Key})
    return opts


def Default_run_set(Session_selector_data, Run_keys_on_date):

    """Determine the default run key to select based on the session selector data and the available runs for the selected date."""

    Most_recent_run_key = Session_selector_data.get("Most_recent_run_key")
    # Prefer the overall most recent run if it exists on the selected date otherwise use the latest run for that date.
    if Run_keys_on_date:
        if Most_recent_run_key in Run_keys_on_date:
            return Most_recent_run_key
        return Run_keys_on_date[-1]
    return Most_recent_run_key


def Build_set_session_select_data(All_sessions_map, Session_overview=None, Session_sort_order="desc"):

    """
    Build all data needed by the date/session selectors and their defaults.

    This is the main setup step that turns raw session data into:
    - date dropdown options
    - session dropdown options
    - default selected date
    - default selected run
    - default selected bed session key

    """

    if Session_overview is None:
        Session_overview = []

    run_group = Build_session_run_map(All_sessions_map)
    Session_run_map = run_group["Session_run_map"]
    Runs_by_date = run_group["Runs_by_date"]
    All_run_keys = run_group["All_run_keys"]

    session_date_list = sorted(Runs_by_date.keys())
    # if the sort order is descending then reverse the session date list so the most recent dates are at the top of the dropdown
    if str(Session_sort_order).lower() == "desc":
        session_date_list = list(reversed(session_date_list))
    session_date_options = [{"label": d, "value": d} for d in session_date_list]

    Most_recent_run_key = All_run_keys[-1] if All_run_keys else None
    Selected_session_date = _extract_session_date(Most_recent_run_key) if Most_recent_run_key else (
        session_date_list[0] if session_date_list else None
    )

    Run_keys_on_date = Filter_runs_by_date({"Runs_by_date": Runs_by_date}, Selected_session_date)
    session_Run_Options = Build_run_options(Run_keys_on_date, {"Session_run_map": Session_run_map}, All_sessions_map)

    Default_session_run_key = Default_run_set({"Most_recent_run_key": Most_recent_run_key}, Run_keys_on_date)
    Default_run_bed_keys = Pull_run_bed_keys({"Session_run_map": Session_run_map}, Default_session_run_key)
    Default_session_key = Default_run_bed_keys[0] if Default_run_bed_keys else None

    return {
        "Session_sort_order": Session_sort_order,
        "session_date_options": session_date_options,
        "Selected_session_date": Selected_session_date,
        "Session_run_map": Session_run_map,
        "Runs_by_date": Runs_by_date,
        "All_run_keys": All_run_keys,
        "Most_recent_run_key": Most_recent_run_key,
        "Run_keys_on_date": Run_keys_on_date,
        "session_Run_Options": session_Run_Options,
        "Default_session_run_key": Default_session_run_key,
        "Default_run_bed_keys": Default_run_bed_keys,
        "Default_session_key": Default_session_key,
    }


###############################################################

def click_nav_history(App_state):

    """
    Save the current navigation state before drilling down to a deeper view.

    This allows the Back button to restore the previous view and selection.

    """

    hist = list(App_state.get("Nav_history", []))
    hist.append({
        "Current_view": App_state.get("Current_view", "overview"),
        "Selected_session_key": App_state.get("Selected_session_key"),
        "Selected_point_id": App_state.get("Selected_point_id"),
        "Selected_sensor_name": App_state.get("Selected_sensor_name"),
        "page_index": _safe_int(App_state.get("page_index", 0), 0),
        "Selected_session_date": App_state.get("Selected_session_date"),
        "Selected_session_run_key": App_state.get("Selected_session_run_key"),
    })
    App_state["Nav_history"] = hist
    return App_state


def pop_nav_history(App_state):
    # Pop the most recent saved navigation state. If no history exists, return None as the previous state.
    hist = list(App_state.get("Nav_history", []))
    if not hist:
        return App_state, None
    prev = hist[-1]
    App_state["Nav_history"] = hist[:-1]
    return App_state, prev


def Build_startup_app_state(Session_selector_data=None):

    """
    Create the initial app state used by the whole interface.

    The store keeps track of:
    - which view is open
    - which bed/point/sensor is selected
    - page number
    - navigation history
    - dropdown selections
    """

    Default_session_key = None
    Default_session_run_key = None
    Selected_session_date = None

    # If session selector data is available, initialise the default date, run, and session selections from it.
    if Session_selector_data:
        Default_session_key = Session_selector_data.get("Default_session_key")
        Default_session_run_key = Session_selector_data.get("Default_session_run_key")
        Selected_session_date = Session_selector_data.get("Selected_session_date")

    return {
        "Current_view": "overview",
        "Selected_session_key": Default_session_key,
        "Selected_point_id": None,
        "Selected_sensor_name": None,
        "Nav_history": [],
        "page_index": 0,
        "Beds_per_page": 8,
        "Selected_session_date": Selected_session_date,
        "Selected_session_run_key": Default_session_run_key,
        "Click_nonce": 0,
    }


def Set_app_state_home(App_state):
    """
    Reset the app to the home overview view.
    """
    App_state["Current_view"] = "overview"
    App_state["Selected_point_id"] = None
    App_state["Selected_sensor_name"] = None
    App_state["Nav_history"] = []
    App_state["page_index"] = 0
    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


def Set_app_state_overview(App_state):
    """
    Return to overview without changing the selected bed/run/date.
    """
    App_state["Current_view"] = "overview"
    App_state["Selected_point_id"] = None
    App_state["Selected_sensor_name"] = None
    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


def Set_app_state_bed(App_state, Selected_session_key):
    """
    Open the selected bed view and update related date/run selections.
    """
    App_state["Current_view"] = "bed"
    App_state["Selected_session_key"] = Selected_session_key
    App_state["Selected_point_id"] = None
    App_state["Selected_sensor_name"] = None

    parts = _split_session_key(Selected_session_key)
    dt = _extract_session_date(parts.get("TimeStamp"))
    # Update the selected date and run to match the chosen session key so the dropdowns stay in sync with the current bed.

    if dt is not None:
        App_state["Selected_session_date"] = dt
    if parts.get("TimeStamp") is not None:
        App_state["Selected_session_run_key"] = parts.get("TimeStamp")

    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


def Set_app_state_point(App_state, Selected_point_id):
    """
    Open the selected point view for the current bed.
    """
    App_state["Current_view"] = "point"
    App_state["Selected_point_id"] = Selected_point_id
    App_state["Selected_sensor_name"] = None
    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


def Set_app_state_sensor(App_state, Selected_sensor_name):
    """
    Open the full single-sensor view after clicking a subplot title.
    """
    App_state["Current_view"] = "single_sensor_full"
    App_state["Selected_sensor_name"] = Selected_sensor_name
    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


def Set_app_state_back(App_state):
    """
    Restore the previous state from navigation history.

    If no history exists, return to overview.
    """
    App_state, Prev_state = pop_nav_history(App_state)
    if Prev_state is None:
        return Set_app_state_overview(App_state)

    App_state["Current_view"] = Prev_state.get("Current_view", "overview")
    App_state["Selected_session_key"] = Prev_state.get("Selected_session_key", App_state.get("Selected_session_key"))
    App_state["Selected_point_id"] = Prev_state.get("Selected_point_id", None)
    App_state["Selected_sensor_name"] = Prev_state.get("Selected_sensor_name", None)
    App_state["page_index"] = _safe_int(Prev_state.get("page_index", App_state.get("page_index", 0)), 0)

    if "Selected_session_date" in Prev_state:
        App_state["Selected_session_date"] = Prev_state.get("Selected_session_date")
    if "Selected_session_run_key" in Prev_state:
        App_state["Selected_session_run_key"] = Prev_state.get("Selected_session_run_key")

    App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
    return App_state


###############################################################

def Get_Page_Count(page_keys, Beds_per_page):
    """Calculate the total number of pages needed for the given bed keys and beds-per-page setting."""
    Beds_per_page = max(1, _safe_int(Beds_per_page, 8))
    n_keys = len(page_keys) if isinstance(page_keys, list) else 0
    return max(1, (n_keys + Beds_per_page - 1) // Beds_per_page)


def Build_Overview_pages(page_keys, Beds_per_page, page_index):
    """
    Convert the full list of bed keys into a single page of keys to display.

    This is used for the overview bed card grid.
    """
    Beds_per_page = max(1, _safe_int(Beds_per_page, 8))
    page_count = Get_Page_Count(page_keys, Beds_per_page)

    page_index = _safe_int(page_index, 0)
    page_index = max(0, min(page_index, page_count - 1))

    start_i = page_index * Beds_per_page
    end_i = start_i + Beds_per_page
    return {"page_index": page_index, "page_count": page_count, "page_keys": list(page_keys[start_i:end_i])}


def Build_Page_Button(page_index, page_count):
    return {"txt_page_status": f"Page {page_index + 1} / {page_count}"}


###############################################################

def Build_overview_cards(All_sessions_map, App_state, Session_selector_data):
    """
    Build the overview grid of bed cards for the currently selected run.

    Each card summarises one bed and allows the user to drill into that bed.
    """
    Selected_session_run_key = App_state.get("Selected_session_run_key")
    Selected_session_key = App_state.get("Selected_session_key")
    Beds_per_page = _safe_int(App_state.get("Beds_per_page", 8), 8)
    page_index = _safe_int(App_state.get("page_index", 0), 0)

    run_bed_keys = Pull_run_bed_keys(Session_selector_data, Selected_session_run_key)
    run_bed_keys = sorted(list(run_bed_keys or []), key=_bed_sort_key_from_session_key)
    # If no bed sessions exist for the selected run, show a message instead of the overview grid.

    if not run_bed_keys:
        return html.Div("No beds exist for this run/date selection.", className="empty")

    page_info = Build_Overview_pages(run_bed_keys, Beds_per_page=Beds_per_page, page_index=page_index)
    page_keys = page_info["page_keys"]

    cards = []
    # Build one clickable card per bed on the current page.
    for Session_Key in page_keys:
        bed_vis = All_sessions_map.get(Session_Key, {}) or {}
        Bed_ID = str(bed_vis.get("Bed_ID", "UNKNOWN"))
        TimeStamp = str(bed_vis.get("TimeStamp", "UNKNOWN"))
        Complete = _safe_int(bed_vis.get("Complete", 0), 0)
        bed_colour = str(bed_vis.get("Bed_colour_grading", "grey")).lower()

        overview = bed_vis.get("Bed_status_summary", {}) if isinstance(bed_vis.get("Bed_status_summary", {}), dict) else {}
        n_present = overview.get("n_points_present", None)
        n_expected = overview.get("n_points_expected", None)

        subtitle_bits = [f"Run: {TimeStamp}", ("Complete" if Complete == 1 else "In Progress")]
        # Only show the points count when both present and expected values are available.
        if n_present is not None and n_expected is not None:
            subtitle_bits.append(f"Points: {n_present}/{n_expected}")

        selected = (Session_Key == Selected_session_key)

        cards.append(
            html.Button(
                [
                    html.Div(Bed_ID, className="tile-title"),
                    html.Div(bed_colour.upper(), className="tile-badge"),
                    html.Div(" | ".join(subtitle_bits), className="tile-subtitle"),
                ],
                id={"type": "bed-card", "session_key": Session_Key},
                n_clicks=0,
                className="tile-card " + _status_class_from_colour(bed_colour) + (" selected" if selected else ""),
            )
        )

    return html.Div(cards, className="tile-grid")


def Build_bed_point_tiles(All_sessions_map, App_state):
    """
    Build the bed view showing clickable point tiles for the selected bed.

    This is the next drill-down level after the overview cards.
    """
    Selected_session_key = App_state.get("Selected_session_key")
    # If the selected session key is missing or invalid, show a fallback message.

    if not Selected_session_key or Selected_session_key not in All_sessions_map:
        return html.Div("No bed selected.", className="empty")

    Bed_visual = All_sessions_map.get(Selected_session_key, {}) or {}
    Bed_ID = str(Bed_visual.get("Bed_ID", "UNKNOWN"))
    TimeStamp = str(Bed_visual.get("TimeStamp", "UNKNOWN"))
    bed_colour = str(Bed_visual.get("Bed_colour_grading", "grey")).lower()
    Complete = _safe_int(Bed_visual.get("Complete", 0), 0)

    Point_colour_map = Bed_visual.get("Point_colour_map", {}) if isinstance(Bed_visual.get("Point_colour_map", {}), dict) else {}

    header = html.Div(
        [
            html.Div(f"{Bed_ID}", style={"fontWeight": "800", "fontSize": "16px"}),
            html.Div(
                f"Run: {TimeStamp} | Bed: {bed_colour.upper()} | {'Complete' if Complete == 1 else 'In Progress'}",
                style={"color": "rgba(255,255,255,0.72)", "fontSize": "12px", "marginTop": "4px"}
            ),
            html.Div("Click a point to open sensor plots.",
                     style={"color": "rgba(255,255,255,0.72)", "fontSize": "12px", "marginTop": "4px"})
        ],
        style={"marginBottom": "10px"}
    )

    tiles = []
    for pid in [1, 2, 3, 4, 5, 6]:
        point_colour = str(Point_colour_map.get(pid, "grey")).lower()
        tiles.append(
            html.Button(
                [
                    html.Div(f"P{pid}", className="tile-title"),
                    html.Div(point_colour.upper(), className="tile-badge"),
                    html.Div("Click to open plots", className="tile-subtitle"),
                ],
                id={"type": "point-tile", "pid": pid, "session_key": Selected_session_key},
                n_clicks=0,
                className="tile-card tile-compact " + _status_class_from_colour(point_colour) + f" p{pid}",
            )
        )

    return html.Div([header, html.Div(tiles, className="point-grid-uturn")])


###############################################################

def Build_subplot_customdata(Sensor_channel, Point_ID=None, Click_nonce=0):
    """
    Pack metadata into a subplot click target so the graph click callback
    can tell which sensor full-view button was clicked.
    """
    return {"Target": "sensor_fullview_button", "Sensor_channel": Sensor_channel, "Point_ID": Point_ID, "Click_nonce": Click_nonce}


def Set_selected_sensor_name_from_click(clickData, Expected_click_nonce=None):
    """
    Extract the selected sensor name from the graph clickData payload.

    Reject stale clicks by checking the click nonce stored in customdata.
    """

    try:
        point = clickData["points"][0]
    except Exception:
        return None

    click_customdata = point.get("customdata", None)
    if isinstance(click_customdata, list) and click_customdata and isinstance(click_customdata[0], dict):
        click_customdata = click_customdata[0]

    if not isinstance(click_customdata, dict):
        return None

    if click_customdata.get("Target") != "sensor_fullview_button":
        return None

    clicked_nonce = _safe_int(click_customdata.get("Click_nonce"), None)
    expected_nonce = _safe_int(Expected_click_nonce, None)

    if expected_nonce is not None and clicked_nonce != expected_nonce:
        return None

    return click_customdata.get("Sensor_channel")


def _count_threshold_excursions(above_baseline, interp_valid):

    """Count the number of times the signal goes above the baseline threshold while being valid."""

    if not isinstance(above_baseline, list) or not isinstance(interp_valid, list):
        return 0
    n = min(len(above_baseline), len(interp_valid))
    count, in_exc = 0, False
    # Count a new excursion only when the signal transitions into an above-threshold valid state.
    for i in range(n):
        a = int(above_baseline[i]) == 1 if above_baseline[i] is not None else False
        v = int(interp_valid[i]) == 1 if interp_valid[i] is not None else False
        is_on = a and v
        if is_on and not in_exc:
            count += 1
            in_exc = True
        elif not is_on:
            in_exc = False
    return count


def _time_above_threshold_s(time_s, above_baseline, interp_valid):

    """Calculate the total time in seconds that the signal is above the baseline threshold while being valid."""
    # Estimate total time above threshold using the sample spacing from time_s.
    if not isinstance(time_s, list) or not time_s:
        return 0.0
    n = min(len(time_s), len(above_baseline or []), len(interp_valid or []))
    if n <= 0:
        return 0.0
    if len(time_s) >= 2:
        dt = _safe_float(time_s[1], 0.0) - _safe_float(time_s[0], 0.0)
        dt = dt if (dt is not None and dt > 0) else 0.0
    else:
        dt = 0.0
    total = 0.0
    for i in range(n):
        a = int(above_baseline[i]) == 1 if above_baseline[i] is not None else False
        v = int(interp_valid[i]) == 1 if interp_valid[i] is not None else False
        if a and v:
            total += dt
    return float(total)


def _combined_min_max(*series_lists):
    # Combine multiple lists of values and calculate the overall minimum and maximum ignoring non-numeric values.
    all_vals = []
    for series in series_lists:
        if isinstance(series, list):
            for v in series:
                fv = _safe_float(v, None)
                if fv is not None:
                    all_vals.append(fv)
    if not all_vals:
        return None, None
    return min(all_vals), max(all_vals)


def Build_point_detail_view(Bed_visual, Selected_point_id, Baseline_thresholds=None, Click_nonce=0):

    """
    Build the 2x3 subplot point view showing all sensors for one selected point.

    Each subplot shows:
    - raw values
    - interpolated values
    - points above threshold
    - threshold lines
    - a clickable [Full] title area to open a single sensor view
    """

    pid = _safe_int(Selected_point_id, 0)

    point_sumup = {}
    # check that the data we expect is actually in the structure
    # and of the right type before we try to access it

    if isinstance(Bed_visual.get("Bed_point_sumup", {}), dict):
        point_sumup = Bed_visual.get("Bed_point_sumup", {}).get(pid, {}) or {}

    Reading_spikes_out = point_sumup.get("Reading_spikes_out", {})
    time_s = list(Reading_spikes_out.get("time_s", []))
    channels = Reading_spikes_out.get("channels", {})

    sensor_order = ["Temp_Air", "Humi_Air", "CO2_ppm", "NH3_ppm", "H2S_ppm", "CH4_Vout"]
    Baseline_thresholds = Baseline_thresholds or {}

    # If time or channel data is missing, return an empty figure with a message.

    if not channels or not time_s:
        fig = go.Figure()
        fig.add_annotation(x=0.5, y=0.5, xref="paper", yref="paper",
                           text=f"No sensor plot data available for P{pid}", showarrow=False)
        fig.update_layout(title=f"Point Detail | {Bed_visual.get('Bed_ID', 'UNKNOWN')} | P{pid}",
                          width=1000, height=650)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig

    fig = make_subplots(rows=2, cols=3, horizontal_spacing=0.08, vertical_spacing=0.16)
    # we iterate through the sensors in the defined order and add traces to the corresponding subplot
    # for each sensor that has data.
    for idx, sensor_name in enumerate(sensor_order):
        r = (idx // 3) + 1
        c = (idx % 3) + 1
        if sensor_name not in channels:
            continue

        ch = channels[sensor_name]
        raw_values = list(ch.get("raw_values", []))
        interp_values = list(ch.get("interp_values", []))
        interp_valid = list(ch.get("interp_valid", []))
        above_baseline = list(ch.get("above_baseline", []))

        fig.add_trace(go.Scatter(
            x=time_s, y=raw_values, mode="lines", showlegend=False,
            hovertemplate="t=%{x}s<br>raw=%{y}<extra></extra>"
        ), row=r, col=c)

        fig.add_trace(go.Scatter(
            x=time_s, y=interp_values, mode="lines", showlegend=False,
            line=dict(dash="dot"),
            hovertemplate="t=%{x}s<br>interp=%{y}<extra></extra>"
        ), row=r, col=c)

        spike_x, spike_y = [], []
        n = min(len(time_s), len(interp_values), len(above_baseline), len(interp_valid))

        # to show the points above threshold we iterate through the above_baseline and interp_valid
        #  lists and collect the time and value for each point where the signal is above threshold and valid.
        for i in range(n):
            is_above = int(above_baseline[i]) == 1 if above_baseline[i] is not None else False
            is_valid = int(interp_valid[i]) == 1 if interp_valid[i] is not None else False
            if is_above and is_valid and interp_values[i] is not None:
                spike_x.append(time_s[i])
                spike_y.append(interp_values[i])

        if spike_x:
            fig.add_trace(go.Scatter(
                x=spike_x, y=spike_y, mode="markers", showlegend=False, marker=dict(size=6),
                hovertemplate="t=%{x}s<br>above=%{y}<extra></extra>"
            ), row=r, col=c)

        th = Baseline_thresholds.get(sensor_name, {})
        tmin, tmax = th.get("Min"), th.get("Max")
        if tmax is not None:
            fig.add_hline(y=float(tmax), line_width=1.5, line_dash="dash", line_color="red", row=r, col=c)
        if tmin is not None:
            fig.add_hline(y=float(tmin), line_width=1.0, line_dash="dot", line_color="red", row=r, col=c)

        label = SENSOR_LABELS.get(sensor_name, sensor_name)
        fig.update_xaxes(title_text="t (s)", row=r, col=c)
        fig.update_yaxes(title_text=label, row=r, col=c)

        x_min = _safe_float(min(time_s), 0.0)
        x_max = _safe_float(max(time_s), 1.0)
        if x_max <= x_min:
            x_max = x_min + 1.0

        y_min, y_max = _combined_min_max(raw_values, interp_values)
        if y_min is None or y_max is None:
            y_min, y_max = 0.0, 1.0
        if y_max <= y_min:
            y_max = y_min + 1.0
        y_span = max(1e-9, (y_max - y_min))

        title_band_h = 0.22 * y_span
        top_pad = 0.08 * y_span
        fig.update_yaxes(range=[y_min - 0.05 * y_span, y_max + top_pad + title_band_h], row=r, col=c)

        title_y0 = y_max + top_pad
        title_y1 = title_y0 + title_band_h
        title_text_y = title_y0 + 0.5 * title_band_h

        title_x0 = x_min + 0.52 * (x_max - x_min)
        title_x1 = x_max
        title_text_x = (title_x0 + title_x1) / 2.0

        fig.add_trace(go.Scatter(
            x=[title_text_x],
            y=[title_text_y],
            mode="text",
            text=[f"{label} [Full]"],
            hoverinfo="skip",
            showlegend=False
        ), row=r, col=c)

        xs, ys = _rect_poly_xy(title_x0, title_y0, title_x1, title_y1)
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", fill="toself",
            line=dict(color="rgba(0,0,0,0)", width=0.1),
            fillcolor="rgba(0,0,0,0)",
            hoveron="fills",
            hoverinfo="text",
            hovertext=f"Open full view for {label}",
            customdata=[Build_subplot_customdata(sensor_name, pid, Click_nonce)] * len(xs),
            showlegend=False
        ), row=r, col=c)

    Bed_ID = str(Bed_visual.get("Bed_ID", "UNKNOWN"))
    TimeStamp = str(Bed_visual.get("TimeStamp", "UNKNOWN"))
    fig.update_layout(
        title=f"Point Detail | {Bed_ID} | Run: {TimeStamp} | P{pid}",
        autosize=True,
        margin=dict(l=80, r=30, t=85, b=60),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        clickmode="event"
    )
    return fig


def Build_selected_sensor_stats(Bed_visual, Selected_point_id, Selected_sensor_name, Baseline_thresholds=None):
    """
    Build a summary of the selected sensor for the current point.

    This is used to populate the right-hand stats panel in full sensor view.
    """
    stats_out = {
        "Sensor_channel": Selected_sensor_name,
        "Max_value": None, "Peak_time_s": None,
        "Time_above_threshold_s": 0.0,
        "Threshold_excursion_count": 0,
        "Sens_state": "UNKNOWN",
        "Mean_value": None,
        "Valid_sample_count": 0,
        "Valid_sample_ratio": None,
        "Threshold_max": None,
        "Threshold_min": None,
    }
    Baseline_thresholds = Baseline_thresholds or {}

    pid = _safe_int(Selected_point_id, 0)
    point_sumup = {}

    # we need to be careful to check that the data we expect is actually in the structure
    if isinstance(Bed_visual.get("Bed_point_sumup", {}), dict):
        point_sumup = Bed_visual.get("Bed_point_sumup", {}).get(pid, {}) or {}

    point_sensor_summaries = point_sumup.get("Point_sensor_summaries", {})
    if isinstance(point_sensor_summaries, dict) and Selected_sensor_name in point_sensor_summaries:
        sens_summary = point_sensor_summaries.get(Selected_sensor_name, {}) or {}
        stats_out["Sens_state"] = sens_summary.get("Sens_state", stats_out["Sens_state"])

    Reading_spikes_out = point_sumup.get("Reading_spikes_out", {})
    time_s = list(Reading_spikes_out.get("time_s", []))
    channels = Reading_spikes_out.get("channels", {})

    if not isinstance(channels, dict) or Selected_sensor_name not in channels:
        th = Baseline_thresholds.get(Selected_sensor_name, {})
        stats_out["Threshold_max"] = th.get("Max")
        stats_out["Threshold_min"] = th.get("Min")
        return stats_out

    ch = channels.get(Selected_sensor_name, {}) or {}
    interp_values = list(ch.get("interp_values", []))
    interp_valid = list(ch.get("interp_valid", []))
    above_baseline = list(ch.get("above_baseline", []))

    valid_pairs = []
    n = min(len(time_s), len(interp_values), len(interp_valid))
    for i in range(n):
        is_valid = int(interp_valid[i]) == 1 if interp_valid[i] is not None else False
        v = interp_values[i]
        if is_valid and v is not None:
            valid_pairs.append((time_s[i], float(v)))

    if valid_pairs:
        vals = [v for _, v in valid_pairs]
        ts = [t for t, _ in valid_pairs]
        max_idx = max(range(len(vals)), key=lambda i: vals[i])
        stats_out["Max_value"] = vals[max_idx]
        stats_out["Peak_time_s"] = ts[max_idx]
        stats_out["Mean_value"] = statistics.mean(vals)
        stats_out["Valid_sample_count"] = len(vals)
        if interp_values:
            stats_out["Valid_sample_ratio"] = len(vals) / float(len(interp_values))

    stats_out["Threshold_excursion_count"] = _count_threshold_excursions(above_baseline, interp_valid)
    stats_out["Time_above_threshold_s"] = _time_above_threshold_s(time_s, above_baseline, interp_valid)

    th = Baseline_thresholds.get(Selected_sensor_name, {})
    stats_out["Threshold_max"] = th.get("Max")
    stats_out["Threshold_min"] = th.get("Min")
    return stats_out


def Build_selected_sensor_stats_display(Bed_visual, Selected_point_id, Selected_sensor_name, Baseline_thresholds=None):
    """
    Convert the selected sensor stats into a title/body text pair for display.
    """

    if Selected_sensor_name is None:
        return "Sensor Stats", "No sensor selected."

    stats = Build_selected_sensor_stats(Bed_visual, Selected_point_id, Selected_sensor_name, Baseline_thresholds)
    Bed_ID = str(Bed_visual.get("Bed_ID", "UNKNOWN"))
    pid = _safe_int(Selected_point_id, 0)

    def _fmt(v, ndp=3):
        if v is None:
            return "N/A"
        try:
            return f"{float(v):.{ndp}f}"
        except Exception:
            return str(v)


    title = f"{SENSOR_LABELS.get(Selected_sensor_name, Selected_sensor_name)} | {Bed_ID} | P{pid}"
    body = "\n".join([
        f"Run ID: {Bed_visual.get('TimeStamp', 'UNKNOWN')}",
        f"Sensor: {Selected_sensor_name}",
        f"Point: P{pid}",
        "",
        f"Sens_state: {stats.get('Sens_state', 'UNKNOWN')}",
        f"Max_value: {_fmt(stats.get('Max_value'), 4)}",
        f"Peak_time_s: {_fmt(stats.get('Peak_time_s'), 2)}",
        f"Mean_value: {_fmt(stats.get('Mean_value'), 4)}",
        "",
        f"Valid_sample_count: {stats.get('Valid_sample_count', 0)}",
        f"Valid_sample_ratio: {_fmt(stats.get('Valid_sample_ratio'), 3)}",
        "",
        f"Time_above_threshold_s: {_fmt(stats.get('Time_above_threshold_s'), 2)}",
        f"Threshold_excursion_count: {stats.get('Threshold_excursion_count', 0)}",
        "",
        f"Threshold_max: {_fmt(stats.get('Threshold_max'), 4)}",
        f"Threshold_min: {_fmt(stats.get('Threshold_min'), 4)}",
    ])
    return title, body


def Build_single_sensor_view(Bed_visual, Selected_point_id, Selected_sensor_name, Baseline_thresholds=None):
    """
    Build the full single-sensor graph for one point.

    This is the final drill-down view and is shown together with sensor stats.
    """

    Baseline_thresholds = Baseline_thresholds or {}
    pid = _safe_int(Selected_point_id, 0)
    fig = go.Figure()

    point_sumup = {}
    if isinstance(Bed_visual.get("Bed_point_sumup", {}), dict):
        point_sumup = Bed_visual.get("Bed_point_sumup", {}).get(pid, {}) or {}

    Reading_spikes_out = point_sumup.get("Reading_spikes_out", {})
    time_s = list(Reading_spikes_out.get("time_s", []))
    channels = Reading_spikes_out.get("channels", {})

    if not isinstance(channels, dict) or Selected_sensor_name not in channels or not time_s:
        fig.add_annotation(
            x=0.5, y=0.5, xref="paper", yref="paper",
            text=f"No data for {Selected_sensor_name} at P{pid}", showarrow=False
        )
        fig.update_layout(
            title=f"Single Sensor View | {Bed_visual.get('Bed_ID', 'UNKNOWN')} | P{pid} | {Selected_sensor_name}",
            width=1100, height=700, plot_bgcolor="white", paper_bgcolor="white"
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig

    ch = channels.get(Selected_sensor_name, {}) or {}
    raw_values = list(ch.get("raw_values", []))
    interp_values = list(ch.get("interp_values", []))
    interp_valid = list(ch.get("interp_valid", []))
    above_baseline = list(ch.get("above_baseline", []))

    fig.add_trace(go.Scatter(x=time_s, y=raw_values, mode="lines", name="raw"))
    fig.add_trace(go.Scatter(x=time_s, y=interp_values, mode="lines", name="interp", line=dict(dash="dot")))

    spike_x, spike_y = [], []
    n = min(len(time_s), len(interp_values), len(above_baseline), len(interp_valid))
    for i in range(n):
        is_above = int(above_baseline[i]) == 1 if above_baseline[i] is not None else False
        is_valid = int(interp_valid[i]) == 1 if interp_valid[i] is not None else False
        if is_above and is_valid and interp_values[i] is not None:
            spike_x.append(time_s[i])
            spike_y.append(interp_values[i])

    if spike_x:
        fig.add_trace(go.Scatter(x=spike_x, y=spike_y, mode="markers",
                                 name="above-threshold", marker=dict(size=7)))

    th = Baseline_thresholds.get(Selected_sensor_name, {})
    tmin, tmax = th.get("Min"), th.get("Max")
    if tmax is not None:
        fig.add_hline(y=float(tmax), line_width=1.6, line_dash="dash", line_color="red")
    if tmin is not None:
        fig.add_hline(y=float(tmin), line_width=1.0, line_dash="dot", line_color="red")

    Bed_ID = str(Bed_visual.get("Bed_ID", "UNKNOWN"))
    TimeStamp = str(Bed_visual.get("TimeStamp", "UNKNOWN"))
    fig.update_layout(
        title=f"Single Sensor View | {Bed_ID} | Run: {TimeStamp} | P{pid} | {Selected_sensor_name}",
        width=1200,
        height=780,
        margin=dict(l=80, r=30, t=80, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_xaxes(title_text="t (s)")
    fig.update_yaxes(title_text=SENSOR_LABELS.get(Selected_sensor_name, Selected_sensor_name))
    return fig


###############################################################

def Get_Bed_Runs_For_Day(All_sessions_map, App_state, Session_selector_data):

    """
    Find all runs on the selected date for the currently selected bed.

    This is used for the day progression view so the same bed can be shown
    across multiple runs from that day.
    """
    runs = []
    if not isinstance(All_sessions_map, dict) or not isinstance(App_state, dict):
        return runs

    Selected_session_key = App_state.get("Selected_session_key")
    Selected_session_date = App_state.get("Selected_session_date")
    if not Selected_session_key or not Selected_session_date:
        return runs

    selected_parts = _split_session_key(Selected_session_key)
    selected_bed_id = selected_parts.get("Bed_ID")
    if not selected_bed_id:
        return runs

    run_keys_on_date = Filter_runs_by_date(Session_selector_data, Selected_session_date)
    # we iterate through the run keys for the selected date and check if we have a session for the selected bed in that run.
    # If we do then we extract the timestamp and other info to build the list of runs to display.
    for Run_Key in run_keys_on_date:
        candidate_key = f"{selected_bed_id}__{Run_Key}"
        if candidate_key not in All_sessions_map:
            continue

        ts_text = str(All_sessions_map[candidate_key].get("TimeStamp", Run_Key))
        try:
            ts_obj = datetime.strptime(ts_text, "%Y-%m-%d_%H-%M-%S")
        except Exception:
            ts_obj = None

        runs.append({
            "session_key": candidate_key,
            "run_key": Run_Key,
            "timestamp_text": ts_text,
            "timestamp_obj": ts_obj,
            "run_label": _extract_run_label(ts_text),
            "Bed_ID": selected_bed_id,
        })

    def _sort_key(row):
        ts_obj = row.get("timestamp_obj")
        ts_text = str(row.get("timestamp_text", ""))
        return (0, ts_obj, ts_text) if ts_obj is not None else (1, ts_text)

    return sorted(runs, key=_sort_key)


def build_day_progression_display(All_sessions_map, App_state, Session_selector_data):
    """
    Build the horizontal list of bed views showing the same bed across the day.
    """

    runs = Get_Bed_Runs_For_Day(All_sessions_map, App_state, Session_selector_data)
    if not runs:
        return html.Div("No runs available for this bed on the selected date.", className="empty")

    cards = []
    for i, run_row in enumerate(runs):
        session_key = run_row["session_key"]
        content = Build_bed_point_tiles(All_sessions_map, {"Selected_session_key": session_key})

        cards.append(
            html.Div(
                [
                    html.Div(f"{i+1}. {run_row.get('run_label','')} ({run_row.get('timestamp_text','')})",
                             className="day-title"),
                    content,
                ],
                className="day-card"
            )
        )

    return cards


###############################################################



def create_dash_app(
    csv_dir: str,
    host: str = "127.0.0.1",
    port: int = 8050,
    debug: bool = False,
    refresh_ms: int = 10000,
    sampling_period_s: float = 5.0,
    baseline_thresholds: dict | None = None,
    point_classify_params: dict | None = None,
):

    """
    Create and configure the Dash application.

    Responsibilities:
    - define default thresholds and classification settings
    - load processed visual session data
    - prepare shared lookup data
    - build layout
    - register callbacks
    - return the finished app
    """

    CSV_Output_dir = str(csv_dir)
    Sampling_Period = float(sampling_period_s)

    if baseline_thresholds is None:
        baseline_thresholds = {
            "Temp_Air": {"Min": -10.0, "Max": 45.0},
            "Humi_Air": {"Min": 0.0, "Max": 100.0},
            "CO2_ppm": {"Min": 300.0, "Max": 1500.0},
            "NH3_ppm": {"Min": 0.0, "Max": 15.0},
            "H2S_ppm": {"Min": 0.0, "Max": 5.0},
            "CH4_Vout": {"Min": 0.0, "Max": 1.8},
        }

    if point_classify_params is None:
        point_classify_params = {
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

    all_vis = Build_All_session_visual_data(
        CSV_Output_dir=CSV_Output_dir,
        Sampling_Period=Sampling_Period,
        Baseline_thresholds=baseline_thresholds,
        Point_classify_params=point_classify_params,
        Interp_Max_Gap=1
    )

    shared = {
        "All_sessions_map": all_vis.get("All_sessions_map", {}),
        "Session_overview": all_vis.get("Session_overview", []),
    }
    shared["Session_selector_data"] = Build_set_session_select_data(
        shared["All_sessions_map"], shared["Session_overview"], Session_sort_order="desc"
    )

    initial_state = Build_startup_app_state(shared["Session_selector_data"])

    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = "Cubiclean Bed Viewer"

    panel_visible_style = {
        "flex": "1",
        "minWidth": "0px",
        "border": "1px solid rgba(255,255,255,0.18)",
        "borderRadius": "16px",
        "padding": "14px",
        "backgroundColor": "rgba(255,255,255,0.10)",
        "height": "78vh",
        "overflowY": "auto"
    }
    panel_hidden_style = {"display": "none"}

    app.layout = html.Div(
        className="container",
        children=[
            html.Div(
                className="header-title",
                children=[
                    html.Div(
                        className="brand",
                        children=[
                            html.H1("Cubiclean Bed Viewer"),
                            html.P("Date → Session → Bed → Point drill-down"),
                        ],
                    ),
                    html.Div(
                        className="controls",
                        children=[
                            html.Div(
                                className="pill date-pill",
                                children=[
                                    html.Label("Date"),
                                    dcc.Dropdown(
                                        id="dropdown-session-date",
                                        className="cc-dropdown",
                                        options=shared["Session_selector_data"].get("session_date_options", []),
                                        value=shared["Session_selector_data"].get("Selected_session_date"),
                                        clearable=False,
                                        style={"minWidth": "180px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                className="pill session-pill",
                                children=[
                                    html.Label("Session"),
                                    dcc.Dropdown(
                                        id="dropdown-session-run",
                                        className="cc-dropdown cc-dropdown-session",
                                        options=shared["Session_selector_data"].get("session_Run_Options", []),
                                        value=shared["Session_selector_data"].get("Default_session_run_key"),
                                        clearable=False,
                                        style={"minWidth": "80%"},
                                    ),
                                ],
                            ),
                            html.Div(
                                className="pill beds-pill",
                                children=[
                                    html.Label("Beds/page"),
                                    dcc.Dropdown(
                                        id="dropdown-beds-per-page",
                                        className="cc-dropdown",
                                        options=[{"label": str(v), "value": v} for v in [4, 6, 8, 9, 12]],
                                        value=initial_state.get("Beds_per_page", 8),
                                        clearable=False,
                                        style={"minWidth": "140px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),

            dcc.Store(id="store-app-state", data=initial_state),
            dcc.Store(id="store-refresh", data=0),
            dcc.Interval(id="interval-refresh", interval=int(refresh_ms), n_intervals=0),

            html.Div(
                className="panel",
                children=[
                    html.Div(
                        className="panel-title",
                        children=[
                            html.Div(
                                children=[
                                    html.Div("Status", style={"fontSize": "16px", "fontWeight": "650"}),
                                    html.Div(id="view-status-text",
                                             style={"fontSize": "12px", "color": "rgba(255,255,255,0.72)"}),
                                ],
                            ),
                            html.Div(
                                className="nav",
                                children=[
                                    html.Button("Home", id="btn-home", n_clicks=0, className="btn"),
                                    html.Button("Back", id="btn-back", n_clicks=0, className="btn"),
                                    html.Button("Prev", id="btn-page-prev", n_clicks=0, className="btn"),
                                    html.Button("Next", id="btn-page-next", n_clicks=0, className="btn"),
                                    html.Span(id="txt-page-status",
                                              style={"marginLeft": "8px", "color": "rgba(255,255,255,0.72)"}),
                                    html.Button("View Day Progression", id="viewDayProgressionButton",
                                                n_clicks=0, className="btn"),
                                ],
                            ),
                        ],
                    ),

                    html.Div(
                        style={"display": "flex", "gap": "12px", "alignItems": "stretch", "minHeight": "0"},
                        children=[
                            html.Div(
                                style={"flex": "3", "minWidth": "0", "minHeight": "0", "overflowY": "auto"},
                                children=[
                                    html.Div(id="main-content"),
                                    html.Div(
                                        id="graph-card-wrapper",
                                        className="graph-card",
                                        style={"display": "none"},
                                        children=[
                                            dcc.Graph(
                                                id="main-graph",
                                                figure=go.Figure(),
                                                style={"height": "100%", "width": "100%"},
                                                config={"displaylogo": False, "responsive": True}
                                            )
                                        ],
                                    ),
                                    html.Div(id="day-progression-panel", children=[],
                                             style={"display": "none", "marginTop": "10px"})
                                ],
                            ),
                            html.Div(
                                id="panel-sensor-stats",
                                children=[
                                    html.H4("Sensor Stats", id="txt-sensor-stats-title", style={"marginTop": "0"}),
                                    html.Pre(
                                        "Open a point, then click a subplot title '[Full]' to view sensor stats here.",
                                        id="txt-sensor-stats-body",
                                        style={"whiteSpace": "pre-wrap",
                                               "fontFamily": "Consolas, monospace",
                                               "fontSize": "12px"}
                                    )
                                ],
                                style=panel_hidden_style
                            )
                        ],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("store-refresh", "data"),
        Input("interval-refresh", "n_intervals"),
        State("store-app-state", "data"),
    )
    def refresh_data_periodically(n_intervals, app_state):
        """
        Periodically rebuild the processed session data from disk.

        This keeps the viewer updated if new CSVs appear or existing ones change.
        The callback only updates shared data and returns a refresh tick value.
        """
        try:
            all_vis_live = Build_All_session_visual_data(
                CSV_Output_dir=CSV_Output_dir,
                Sampling_Period=Sampling_Period,
                Baseline_thresholds=baseline_thresholds,
                Point_classify_params=point_classify_params,
                Interp_Max_Gap=1
            )
            shared["All_sessions_map"] = all_vis_live.get("All_sessions_map", {})
            shared["Session_overview"] = all_vis_live.get("Session_overview", [])
            shared["Session_selector_data"] = Build_set_session_select_data(
                shared["All_sessions_map"], shared["Session_overview"], Session_sort_order="desc"
            )
        except Exception:
            pass
        return n_intervals

    @app.callback(
        Output("dropdown-session-run", "options"),
        Output("dropdown-session-run", "value"),
        Input("dropdown-session-date", "value"),
        Input("store-refresh", "data"),
        State("store-app-state", "data"),
    )
    def update_run_dropdown_from_date(selected_date, _refresh_tick, app_state):
        """
        Update the session dropdown whenever:
        - the selected date changes
        - data refresh occurs

        If refresh triggered the callback, keep the current dropdown value where possible.
        """
        ss = shared["Session_selector_data"]
        asm = shared["All_sessions_map"]

        run_keys = Filter_runs_by_date(ss, selected_date)
        opts = Build_run_options(run_keys, ss, asm)

        trig = _get_triggered_id()
        if trig == "store-refresh":
            return opts, no_update

        current = (app_state or {}).get("Selected_session_run_key")
        if current in run_keys:
            return opts, current

        return opts, Default_run_set(ss, run_keys)

    @app.callback(
        Output("store-app-state", "data"),
        Input("main-graph", "clickData"),
        Input("btn-home", "n_clicks"),
        Input("btn-back", "n_clicks"),
        Input("dropdown-session-date", "value"),
        Input("dropdown-session-run", "value"),
        Input("dropdown-beds-per-page", "value"),
        Input("btn-page-prev", "n_clicks"),
        Input("btn-page-next", "n_clicks"),
        Input("viewDayProgressionButton", "n_clicks"),
        Input({"type": "bed-card", "session_key": ALL}, "n_clicks"),
        Input({"type": "point-tile", "pid": ALL, "session_key": ALL}, "n_clicks"),
        State("store-app-state", "data"),
        prevent_initial_call=True
    )
    def update_app_state(
        clickData,
        n_home,
        n_back,
        Selected_dates_value,
        Selected_run_value,
        Beds_per_page_value,
        Page_prev_click,
        Page_next_click,
        view_day_progression_click,
        bed_card_clicks,
        point_tile_clicks,
        App_state
    ):
        """
        Main control callback for the application.

        This callback listens to all user interactions that change navigation state.
        It updates the stored app state, but does not render the page directly.
        Rendering is handled separately by render_from_state().
        """
        asm = shared["All_sessions_map"]
        ss = shared["Session_selector_data"]

        if App_state is None:
            App_state = Build_startup_app_state(ss)

        trig = _get_triggered_id()

        App_state["Beds_per_page"] = _safe_int(Beds_per_page_value, App_state.get("Beds_per_page", 8))
        App_state["Selected_session_date"] = Selected_dates_value

        if trig == "btn-home":
            return Set_app_state_home(App_state)

        if trig == "btn-back":
            return Set_app_state_back(App_state)

        if trig == "dropdown-session-date":
            App_state["page_index"] = 0
            App_state["Selected_session_date"] = Selected_dates_value
            run_keys = Filter_runs_by_date(ss, Selected_dates_value)
            default_run = Default_run_set(ss, run_keys)
            App_state["Selected_session_run_key"] = default_run
            run_bed_keys = Pull_run_bed_keys(ss, default_run)
            if run_bed_keys:
                App_state["Selected_session_key"] = run_bed_keys[0]
            return Set_app_state_overview(App_state)

        if trig == "dropdown-session-run":
            App_state["page_index"] = 0
            App_state["Selected_session_run_key"] = Selected_run_value
            run_bed_keys = Pull_run_bed_keys(ss, Selected_run_value)
            if run_bed_keys and App_state.get("Selected_session_key") not in run_bed_keys:
                App_state["Selected_session_key"] = run_bed_keys[0]
            return Set_app_state_overview(App_state)

        if trig == "dropdown-beds-per-page":
            App_state["page_index"] = 0
            return Set_app_state_overview(App_state)

        if trig in ["btn-page-prev", "btn-page-next"]:
            page_index = _safe_int(App_state.get("page_index", 0), 0)
            run_key = App_state.get("Selected_session_run_key")
            run_bed_keys = Pull_run_bed_keys(ss, run_key)
            base_keys = sorted(list(run_bed_keys or []), key=_bed_sort_key_from_session_key)
            if not base_keys:
                App_state["page_index"] = 0
                return App_state

            page_info = Build_Overview_pages(base_keys, _safe_int(App_state.get("Beds_per_page", 8), 8), page_index)
            page_index = page_info["page_index"]
            page_count = page_info["page_count"]

            if trig == "btn-page-prev" and page_index > 0:
                page_index -= 1
            elif trig == "btn-page-next" and page_index < page_count - 1:
                page_index += 1

            App_state["page_index"] = page_index
            App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
            return App_state

        if trig == "viewDayProgressionButton":
            if App_state.get("Current_view") in ["bed", "day_progression"] and App_state.get("Selected_session_key") in asm:
                App_state = click_nav_history(App_state)
                App_state["Current_view"] = "day_progression"
                App_state["Selected_sensor_name"] = None
                App_state["Click_nonce"] = _safe_int(App_state.get("Click_nonce", 0), 0) + 1
            return App_state

        if isinstance(trig, dict) and trig.get("type") == "bed-card":
            bed_clicks = _pattern_click_count(trig)
            if bed_clicks <= 0:
                return App_state

            sk = trig.get("session_key")
            if sk in asm:
                App_state = click_nav_history(App_state)
                return Set_app_state_bed(App_state, sk)
            return App_state

        if isinstance(trig, dict) and trig.get("type") == "point-tile":
            point_clicks = _pattern_click_count(trig)
            if point_clicks <= 0:
                return App_state

            pid = _safe_int(trig.get("pid"), None)
            sk = trig.get("session_key")

            if sk:
                App_state["Selected_session_key"] = sk

            if pid is not None:
                App_state = click_nav_history(App_state)
                return Set_app_state_point(App_state, pid)

            return App_state

        if trig == "main-graph" and clickData is not None:
            if App_state.get("Current_view") == "point":
                s = Set_selected_sensor_name_from_click(
                    clickData,
                    Expected_click_nonce=App_state.get("Click_nonce", 0)
                )
                if s:
                    App_state = click_nav_history(App_state)
                    return Set_app_state_sensor(App_state, s)

        return App_state

    @app.callback(
        Output("main-content", "children"),
        Output("main-content", "style"),
        Output("main-graph", "figure"),
        Output("graph-card-wrapper", "style"),
        Output("main-graph", "clickData"),
        Output("txt-page-status", "children"),
        Output("btn-page-prev", "style"),
        Output("btn-page-next", "style"),
        Output("viewDayProgressionButton", "style"),
        Output("txt-sensor-stats-title", "children"),
        Output("txt-sensor-stats-body", "children"),
        Output("panel-sensor-stats", "style"),
        Output("day-progression-panel", "children"),
        Output("day-progression-panel", "style"),
        Input("store-app-state", "data"),
        Input("store-refresh", "data"),
    )
    def render_from_state(App_state, _refresh_tick):

        """
        Render the visible UI from the current stored app state.

        This callback decides:
        - what main content to show
        - whether a graph should be visible
        - whether paging buttons should show
        - whether the day progression panel should show
        - whether the sensor stats panel should show
        """

        asm = shared["All_sessions_map"]
        ss = shared["Session_selector_data"]

        if App_state is None:
            App_state = initial_state

        Current_view = App_state.get("Current_view", "overview")
        Selected_session_key = App_state.get("Selected_session_key")
        Selected_point_id = App_state.get("Selected_point_id")
        Selected_sensor_name = App_state.get("Selected_sensor_name")
        Selected_session_run_key = App_state.get("Selected_session_run_key")
        Beds_per_page = _safe_int(App_state.get("Beds_per_page", 8), 8)
        page_index = _safe_int(App_state.get("page_index", 0), 0)

        run_bed_keys = Pull_run_bed_keys(ss, Selected_session_run_key)
        run_bed_keys = sorted(list(run_bed_keys or []), key=_bed_sort_key_from_session_key)

        view_session_key = Selected_session_key
        if Current_view in ["overview", "bed", "day_progression"]:
            if run_bed_keys and view_session_key not in run_bed_keys:
                view_session_key = run_bed_keys[0] if run_bed_keys else view_session_key

        page_info = Build_Overview_pages(run_bed_keys, Beds_per_page, page_index) if run_bed_keys else {"page_index": 0, "page_count": 1}
        page_status = Build_Page_Button(page_info["page_index"], page_info["page_count"])["txt_page_status"]

        show_paging = page_info["page_count"] > 1
        prev_btn_style = {} if show_paging else {"display": "none"}
        next_btn_style = {} if show_paging else {"display": "none"}
        show_day_btn = Current_view in ["bed", "day_progression"]
        day_btn_style = {} if show_day_btn else {"display": "none"}

        stats_title = "Sensor Stats"
        stats_body = "Open a point, then click a subplot title '[Full]' to view sensor stats here."
        panel_style_out = panel_hidden_style

        day_children = []
        day_style = {"display": "none"}

        main_children = []
        main_style = {"display": "block"}
        graph_fig = go.Figure()
        graph_style = {"display": "none"}

        # The main content rendering logic is based on the Current_view in the app state.

        if Current_view == "overview":
            tmp_state = dict(App_state)
            tmp_state["Selected_session_key"] = view_session_key
            main_children = Build_overview_cards(asm, tmp_state, ss)
            main_style = {"display": "block"}

        elif Current_view == "bed":
            tmp_state = dict(App_state)
            tmp_state["Selected_session_key"] = view_session_key
            main_children = Build_bed_point_tiles(asm, tmp_state)
            main_style = {"display": "block"}

        elif Current_view == "day_progression":
            tmp_state = dict(App_state)
            tmp_state["Selected_session_key"] = view_session_key
            main_children = Build_bed_point_tiles(asm, tmp_state)
            main_style = {"display": "block"}
            day_children = build_day_progression_display(asm, tmp_state, ss)
            day_style = {
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "gap": "12px",
                "marginTop": "10px",
                "width": "100%",
                "overflowX": "auto",
                "overflowY": "hidden",
                "paddingBottom": "10px",
                "alignItems": "stretch"
            }

        elif Current_view == "point":
            if Selected_session_key in asm and Selected_point_id is not None:
                graph_fig = Build_point_detail_view(
                    asm[Selected_session_key],
                    Selected_point_id,
                    Baseline_thresholds=baseline_thresholds,
                    Click_nonce=_safe_int(App_state.get("Click_nonce", 0), 0)
                )
                main_children = []
                main_style = {"display": "none"}
                graph_style = {"display": "block"}
            else:
                main_children = html.Div("Selected point/session no longer available.", className="empty")
                main_style = {"display": "block"}

        elif Current_view == "single_sensor_full":
            panel_style_out = panel_visible_style
            if Selected_session_key in asm and Selected_point_id is not None and Selected_sensor_name:
                graph_fig = Build_single_sensor_view(
                    asm[Selected_session_key],
                    Selected_point_id,
                    Selected_sensor_name,
                    Baseline_thresholds=baseline_thresholds
                )
                stats_title, stats_body = Build_selected_sensor_stats_display(
                    asm[Selected_session_key],
                    Selected_point_id,
                    Selected_sensor_name,
                    Baseline_thresholds=baseline_thresholds
                )
                main_children = []
                main_style = {"display": "none"}
                graph_style = {"display": "block"}
            else:
                main_children = html.Div("Selected sensor/session no longer available.", className="empty")
                main_style = {"display": "block"}
                panel_style_out = panel_hidden_style

        return (
            main_children,
            main_style,
            graph_fig,
            graph_style,
            None,
            page_status,
            prev_btn_style,
            next_btn_style,
            day_btn_style,
            stats_title,
            stats_body,
            panel_style_out,
            day_children,
            day_style
        )

    return app, host, port, debug


def run_dash_app(
    csv_dir: str,
    host: str = "127.0.0.1",
    port: int = 8050,
    debug: bool = False,
    refresh_ms: int = 10000,
    sampling_period_s: float = 5.0,
    baseline_thresholds: dict | None = None,
    point_classify_params: dict | None = None,
):
    app, h, p, d = create_dash_app(
        csv_dir=csv_dir,
        host=host,
        port=port,
        debug=debug,
        refresh_ms=refresh_ms,
        sampling_period_s=sampling_period_s,
        baseline_thresholds=baseline_thresholds,
        point_classify_params=point_classify_params,
    )
    app.run(host=h, port=p, debug=d)


if __name__ == "__main__":
    run_dash_app(
        csv_dir=r"C:\Users\brand\source\repos\out_mock",
        host="10.224.242.1",
        port=8050,
        debug=False,
        refresh_ms=10000
    )