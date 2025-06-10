# Constant Definitons
#
# Provides a set of constant variables used in lookup_agenda.py and
# import_agenda.py. Constants are either numeric constants, error constants,
# or constants that define the columns used for a specific task
#

# numeric constants
ROWS_TO_SKIP = 14

# error constants
IMPORT_INCORRECT_ARG_AMOUNT_ERROR = "Expected 1 additional argument with xls file path"
IMPORT_INVALID_PATH_ERROR = "Provided an invalid path"
IMPORT_INVALID_FILENAME_ERROR = "Invalid xls file name"
LOOKUP_NOT_ENOUGH_ARGS_ERROR = "Expected 2 or more additional arguments with column and value"
LOOKUP_INVALID_COLUMN_ERROR = "Invalid query column"

#
# Excel columns
# A list of column names used when importing data from an Excel sheet
# These columns correspond to the fields in the agenda
#
EXCEL_COLUMNS = [
    "date",
    "time_start",
    "time_end",
    "session_type",
    "title",
    "location",
    "description",
    "speakers"
]

#
# Sessions columns
# A list of the columns in the agenda that are directly inserted
# into the session table
#
SESSIONS_COLUMNS = [
    "date",
    "time_start",
    "time_end",
    "title",
    "location",
    "description",
]

#
# Query columns
# A list of valid column names that can be queried in lookup_agenda.py
#
QUERY_COLUMNS = [
    "date",
    "time_start",
    "time_end",
    "title",
    "location",
    "description",
    "speaker"
]

#
# Query columns
# A list of the columns whose data is printed in lookup_agenda.py if matches
# are found
#
DISPLAY_COLUMNS = [
    "title",
    "date",
    "time_start",
    "time_end",
    "location",
    "description",
]
