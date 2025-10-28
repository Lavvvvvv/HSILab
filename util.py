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
    Simple name-based detection: return columns whose names match common timestamp keywords. Written by copilot
    Returns {'columns': [colnames], 'index': index_name_or_None}
    """

    pattern = re.compile(
    r'(?i)(?:^|(?<=[\W_-]))(?:time|timestamp|ts|date|datetime|start|end)(?:$|(?=[\W_-]))'
    )
    cols = [col for col in df.columns if pattern.search(str(col))]
    idx_name = df.index.name
    index_candidate = idx_name if (idx_name and pattern.search(str(idx_name))) else None
    return {'columns': cols, 'index': index_candidate}


"""
make function to combine files with different timestamps and filling up gaps with 0
"""

def unix2readable_synchronizeData(*csv_paths):
    """
    take 2 or more data (in csv form or pd) sync the data (start from the earliest data) add datapoints in the column the the later starting data, in empty spaces write null or something as a place holder
    """
    dfs = []


    for i, item in enumerate(csv_paths):
        df=pd.read_csv(item)
        time_column=find_timestamp_candidates(df)
        for column_name in column_name:
            df[column_name] = unix_to_readable(df[column_name], unit='ns')
        dfs.append(df)

    


        


    



    