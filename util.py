import numpy as np
import pandas as pd
from datetime import datetime, timezone
import re


try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

def unix_to_readable(ts, fmt='%Y-%m-%d %H:%M:%S', tz='local', unit='s'):
    """
    Convert unix timestamp(s) to human-readable string(s). written by copilot

    Parameters
    - ts: scalar (int/float), list, numpy array, pandas Series or Index
    - fmt: strftime format string
    - tz: 'utc', 'local', None, or an IANA timezone string (e.g. 'Europe/Berlin')
    - unit: 's' (seconds), 'ms' (milliseconds), 'us' (microseconds), 'ns' (nanoseconds)

    Returns
    - scalar string for scalar input
    - list for list/ndarray input
    - pandas.Series or pandas.Index of strings for pandas input
    """
    unit = str(unit)
    scale = {'s': 1, 'ms': 1_000, 'us': 1_000_000, 'ns': 1_000_000_000}
    if unit not in scale:
        raise ValueError("unit must be one of 's', 'ms', 'us', 'ns'")

    def _get_zone(tz_arg):
        if tz_arg == 'utc':
            return timezone.utc
        if tz_arg == 'local' or tz_arg is None:
            return datetime.now().astimezone().tzinfo
        # try zoneinfo
        if isinstance(tz_arg, str):
            if ZoneInfo is not None:
                return ZoneInfo(tz_arg)
            try:
                import pytz
                return pytz.timezone(tz_arg)
            except Exception:
                pass
        return datetime.now().astimezone().tzinfo

    # pandas Series -> use .dt accessor for tz ops and strftime
    if isinstance(ts, pd.Series):
        dt_s = pd.to_datetime(ts, unit=unit, origin='unix', utc=True)  # Series tz-aware UTC
        zone = _get_zone(tz)
        if zone is not None:
            try:
                dt_s = dt_s.dt.tz_convert(zone)
            except Exception:
                dt_s = dt_s.dt.tz_localize('UTC').dt.tz_convert(zone)
        return dt_s.dt.strftime(fmt)

    # pandas Index (DatetimeIndex) -> use Index methods
    if isinstance(ts, pd.Index):
        dt_idx = pd.to_datetime(ts, unit=unit, origin='unix', utc=True)  # tz-aware UTC
        zone = _get_zone(tz)
        if zone is not None:
            try:
                dt_idx = dt_idx.tz_convert(zone)
            except Exception:
                dt_idx = dt_idx.tz_localize('UTC').tz_convert(zone)
        return dt_idx.strftime(fmt)

    if isinstance(ts, (list, tuple, np.ndarray)):
        dt_idx = pd.to_datetime(list(ts), unit=unit, origin='unix', utc=True)
        zone = _get_zone(tz)
        try:
            dt_idx = dt_idx.tz_convert(zone)
        except Exception:
            dt_idx = dt_idx.tz_localize('UTC').tz_convert(zone)
        return dt_idx.strftime(fmt).tolist()

    # scalar path
    if isinstance(ts, (int, float, np.integer, np.floating)):
        seconds = float(ts) / scale[unit]
        zone = _get_zone(tz)
        if isinstance(zone, timezone):
            dt = datetime.fromtimestamp(seconds, tz=zone)
        else:
            # zone can be zoneinfo.ZoneInfo or pytz timezone or tzinfo
            try:
                dt = datetime.fromtimestamp(seconds, tz=timezone.utc).astimezone(zone)
            except Exception:
                dt = datetime.fromtimestamp(seconds)
        return dt.strftime(fmt)

    # last resort: try pandas conversion then format single value
    try:
        dt = pd.to_datetime(ts, origin='unix', unit=unit)
        return dt.strftime(fmt)
    except Exception:
        raise TypeError("Unsupported timestamp type")
    

def find_timestamp_candidates(df):
    """
    Simple name-based detection: return columns whose names match common timestamp keywords.
    Returns list of candidate timestamp column names, we get every column names that has to do with time.
    """

    pattern = re.compile(
    r'(?i)(?:^|(?<=[\W/_-]))(?:time|timestamp(?:\s*\[ns\])?|ts)(?:$|(?=[\W/_-]))'
)

    cols = [col for col in df.columns if pattern.search(str(col))]
    
    return cols


"""
make function to combine files with different timestamps and filling up gaps with 0
"""

def synchronize_data(*csv_paths):
    """
    take 2 or more data (in csv form or pd) sync the data (start from the earliest data) add datapoints in the column the the later starting data, in empty spaces write null or something as a place holder
    """
    dfs = {} #{"argorder" : pd series}, 
    
    #check if the passed arguments are strings or dfs, get a dfs only with the timestamps, right now only checking the index 2 element
    if isinstance(csv_paths[0],str):
        for i, path in enumerate(csv_paths):
            df=pd.read_csv(path, sep=';')
            time_column=find_timestamp_candidates(df) 
            #we take the first one in the list as the timestamp of the recording.
            time_column=time_column[0]
            df=df[time_column]
            dfs={'{i}':df}
            
    else:
        for j, df in enumerate(csv_paths):
            time_column=find_timestamp_candidates(df) 
            time_column=time_column[0]
            df=df[time_column]
            dfs={'{j}':df}

    print(dfs)




    """
    1. check which one has the most datapoints (higher sampling frequency)
    2. make that the timestamp of the combined df
    3. make new timestamp if the denset timestamp doesnt have the earliest timestamps (padding)
    4. insert data (padd additional points if data doesnt cover it)
    5. outide of inserted data put null in where there is no data
    """

    length=len(dfs)


eda_path="C:/Users/Susanto/Documents/Personal/Shimmer/shimmer-main/shimmer-main/export/eda2/Shimmer_A0F4-001_000.csv"
ecg_path="C:/Users/Susanto/Documents/Personal/Shimmer/shimmer-main/shimmer-main/export/ecgtest4_1754555732/Shimmer_0000-000_000.csv"
eyestates_path="C:/Users/Susanto/Documents/Personal/pupilLabs/pupilLabs-main/pupilLabs-main/export/2025-06-24-15-38-04/csv/3d_eye_states.csv"

eda_df=pd.read_csv(eda_path, sep=';')
ecg_df=pd.read_csv(ecg_path, sep=';')
eyestates_df=pd.read_csv(eyestates_path, sep=';')

synchronize_data(eda_path,ecg_path,eyestates_path)


    

    


        


    



    