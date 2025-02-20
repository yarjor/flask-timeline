#!usr/bin/python

from datetime import datetime, timedelta
from typing import Any


################################
#      BASE SCRIPT CONSTS      #
################################
# Don't touch unless you know what you are doing!

# Time periods
SECOND = timedelta(seconds=1)
MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
WEEK = timedelta(weeks=1)
MONTH = timedelta(days=30.5)
YEAR = timedelta(days=365.25)

# Conversion between time units and textual name
UNIT_PICKER = {
    'Second(s)' : SECOND,
    'Minute(s)' : MINUTE,
    'Hour(s)' : HOUR,
    'Day(s)' : DAY,
    'Month(s)' : MONTH,
    'Year(s)' : YEAR
}

# Format string for strptime - matches the DatePicker configuration
TIME_FORMAT = '%m/%d/%Y %I:%M %p'

# Bootstrap colors
COLORS = ['default', 'primary', 'success', 'info', 'warning', 'danger']

# Format Strings for SQL queries
QUERY_MATCH = {
    "Title" : "Event.title.ilike('%{txt}%')",
    "Text" : "Event.description.ilike('%{txt}%')",
    "All" : "Event.description.ilike('%{txt}%') | Event.title.ilike('%{txt}%')"
}
NOT_QUERY_MATCH = {
    "Title" : "~Event.title.ilike('%{txt}%')",
    "Text" : "~Event.description.ilike('%{txt}%')",
    "All" : "~Event.description.ilike('%{txt}%') && ~Event.title.ilike('%{txt}%')"
}
TAG_QUERY = "Event.tags.ilike('%{txt}%')"

################################
#     OPTIONAL USER CONSTS     #
################################

# Both must match - use UNIT_PICKER to check the textual name
DEFAULT_TICK = 2 * DAY
TEXTUAL_TICK = [2, 'Day(s)']

# Running HTML port
PORT = 5000

# Security key
APP_KEY = 'development key'

# Empty user config - probably shouldn't touch this
EMPTY_CONFIG: dict[str, Any] = dict(
    tick=DEFAULT_TICK,
    textual_tick=TEXTUAL_TICK,
    start=datetime.min,
    end=datetime.max,
    filter="",
    advanced_filters=[], # sqlalchemy filters, saved in string form (conversion is made when submitting the config)
    required_filters=[],
    text_filters=[],
    tags=[],
    colors=COLORS
    )

################################
#     REQUIRED USER CONSTS     #
################################

# DB where the events are stored, must match the ORM specified in schema.py
DB_NAME = 'TimeLoops.db'

# JSONified list of all ever used tags
# If changed, must change index.js to reference the new file path
ALL_TAGS = r'.\static\alltags.json'
