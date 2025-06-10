#!/usr/bin/env python3

# access command line arguments
import sys

# manipulation of excel data
import pandas as pd

# vectorized array operations
import numpy as np

# file path representation
from pathlib import Path

# access to sqlite wrapper
from db_table import db_table

# access to relevant constants
from constants import (
    ROWS_TO_SKIP,
    IMPORT_INCORRECT_ARG_AMOUNT_ERROR,
    IMPORT_INVALID_PATH_ERROR,
    IMPORT_INVALID_FILENAME_ERROR,
    SESSIONS_COLUMNS,
    EXCEL_COLUMNS
)

# table schema representations
from models import *

#
# Path validator
# Validates the path of the input file by ensuring the script receives
# exactly one additional argument, that the file exists,
# and that the file has the '.xls' extension
#
# \raises ValueError    If the number of arguments is incorrect,
#                       the path is not a file, or the filename is not valid
#
def validate_path():

    # enforce requirement to provide a file as an argument
    argc = len(sys.argv)
    if argc != 2:
        raise ValueError(IMPORT_INCORRECT_ARG_AMOUNT_ERROR)

    # verify that the path exists
    path = Path(sys.argv[1])
    if not path.is_file():
        raise ValueError(IMPORT_INVALID_PATH_ERROR)

    # verify that the file is of the correct type
    if path.suffix != ".xls":
        raise ValueError(IMPORT_INVALID_FILENAME_ERROR )

#
# Session data processor
# Processes session data from the provided dataframe and inserts it into the sessions table
# The function extracts relevant session fields, handles supersessions for "Sub" types,
# and tracks session ids for use in future speaker insertions
#
# \param excel_df        dataframe containing the session data from the Excel file
# \param sessions_table  db_table object for the sessions table
#
# \return np.ndarray     Array of session ids inserted into the sessions table
#
def process_session_data(excel_df, sessions_table):

    # use an np array to hold all session ids
    session_ids = np.empty(len(excel_df), dtype=np.int64)

    # keep track of the last session, since this will serve as the supersession of
    # the next subsession
    last_session_id = None

    # insert each session to the sessions table,
    # making sure to update its supersession_id if its a subsession and
    # to update the last_session_id otherwise
    for index, row in enumerate(excel_df.to_dict("records")):
        session_data = {key: row[key] for key in SESSIONS_COLUMNS if pd.notna(row[key])}

        if row["session_type"] == "Sub":
            session_data["supersession_id"] = last_session_id

        session_ids[index] = sessions_table.insert(session_data)

        if row["session_type"] == "Session":
            last_session_id = session_ids[index]

    return session_ids

#
# Speaker data processor
# Processes speaker data from the provided Excel DataFrame and inserts it into the speakers table
# It matches existing speakers by name or inserts new ones, and associates them with sessions in the sessions_speakers table
#
# \param excel_df                dataframe containing the session data from the Excel file
# \param session_ids             np array of session ids, used to establish relationships betwee speakers and sessions
# \param speakers_table          db_table object for the speakers table
# \param sessions_speakers_table db_table object for the session_speakers table
#
def process_speaker_data(excel_df, session_ids, speakers_table, sessions_speakers_table):

    sessions_speakers = []
    speaker_ids = {}

    # use tuples to iterate through the speakers for performance
    for index, speakers in excel_df.loc[:, ["speakers"]].itertuples():
        if pd.isna(speakers):
            continue

        # convert speaker string into a list of names
        speaker_names = [
            untrimmed_name.strip()
            for untrimmed_name
            in str(speakers).split(";")
        ]

        # collect the ids for each speaker, and only add the speaker to
        # the speakers table if it does not yet exist in the table
        for name in speaker_names:
            sessions_speakers.append((session_ids[index], name))
            speaker_data = {"name":name}

            speakers_match = speakers_table.select(
                columns=["id"],
                where=speaker_data
            )

            if speakers_match:
                speaker_ids[name] = speakers_match[0]["id"]
            else:
                speaker_ids[name] = speakers_table.insert(speaker_data)

    # use the memoized ids to make insertions into the join table
    for session_id, name in sessions_speakers:
        sessions_speakers_table.insert({
            'session_id': session_id,
            'speaker_id': speaker_ids[name]
        })

#
# Driver Program
# Validates the input path, reads the Excel data into a dataframe,
# and calls functions to processes the session and speaker data
# Any exceptions raised during are caught and logged to the standard output
#
def main():
    try:
        validate_path()

        filename = sys.argv[1]

        # use pandas to read excel data
        excel_df = pd.read_excel(
            filename,
            skiprows=ROWS_TO_SKIP,
            names=EXCEL_COLUMNS,
        )

        # create tables based on the existing schemas
        sessions_table = db_table("sessions", sessions_schema)
        speakers_table = db_table("speakers", speakers_schema)
        sessions_speakers_table = db_table("sessions_speakers", sessions_speakers_schema)

        # process and insert all session data
        session_ids = process_session_data(excel_df, sessions_table)

        # use session ids to process and insert speaker data.
        process_speaker_data(excel_df, session_ids, speakers_table, sessions_speakers_table)

    except Exception as e:
        print(f"Error occured: {e}")
        sys.exit(1)

#
# Program entrypoint
# Ensures the program is not being run as a module, then calls
# the main() function to execute the primary functionality.
#
if __name__ == "__main__":
    main()

