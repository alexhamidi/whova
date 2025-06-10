#!/usr/bin/env python3

# access command line arguments
import sys

# access to sqlite wrapper
from db_table import db_table

# access to relevant constants
from constants import (
    LOOKUP_NOT_ENOUGH_ARGS_ERROR,
    LOOKUP_INVALID_COLUMN_ERROR,
    QUERY_COLUMNS,
    DISPLAY_COLUMNS
)

# table schema representations
from models import *

#
# Path validator
# Validates the path of the input query by ensuring that the script receives
# two or more additional arguments and that the provided column is one of:
# {date, time_start, time_end, title, location, description, speaker}
#
# \raises ValueError    If the number of arguments is incorrect or the column is not valid
#
def validate_query():

    # verify that at least 2 additional arguments are provided
    argc = len(sys.argv)
    if argc < 3:
        raise ValueError(LOOKUP_NOT_ENOUGH_ARGS_ERROR)

    column = sys.argv[1]

    # verify that the provided column is a queryable column
    if column not in QUERY_COLUMNS:
        raise ValueError(LOOKUP_INVALID_COLUMN_ERROR)

#
# Query match returner
# Retrieves all sessions that match the given query. If the query is for a speaker name,
# it will return all sessions the speaker attended, including all subsessions.
# It performs a database join between sessions, session_speakers, and speakers tables.
#
# \param column             Column being queried
# \param value              Value to search for in the specified column
# \param sessions_table     db_table object for the sessions table
# \param sessions_speakers  db_table object for the session_speakers table
# \param speakers_table     db_table object for the speakers table
#
# \return list of dicts    Each dict represents a session matching the query or a subsession of a matching session.
#
def get_all_matches(column, value, sessions_table, sessions_speakers_table, speakers_table):
    sessions_match = []

    # if a speaker is queried, use the join table to find all sessions that match
    # the provided speaker
    if (column == "speaker"):
        sessions_match = sessions_table.select(
            join=[
                (sessions_table, sessions_speakers_table, "id", "session_id"),
                (sessions_speakers_table, speakers_table, "speaker_id", "id")
            ],
            where={"name":value}
        )
    # if the query if for a non-speaker column, simply select it from the database.
    else:
        sessions_match = sessions_table.select(where={column:value})

    if not sessions_match:
        raise ValueError("No matches found for the given query.")

    # keep track of all previous ids to get corresponding subsessions
    selected_session_ids = [session["id"] for session in sessions_match]

    # use the IN functionality of db_table to select all sessions
    # that have not yet been selected and that have supersessions that
    # matched the query.
    sessions_match.extend(sessions_table.select(
        where={
            "supersession_id":selected_session_ids,
            "id NOT":selected_session_ids
        }
    ))

    return sessions_match

#
# Speaker name collector
# Returns the names of every speaker attending a given session. Joins the speaker
# and sessions_speaker tables to directly query the speakers associated with a session id.
# Will return an empty array if no speaker is attending the session.
#
# \param session              session for which we are returning the speakers
# \param speakers_table       db_table object for the speakers table
# \param session_speakers_table       db_table object for the session_speakers table
#
# \return list of speaker name strings.
#
def get_speaker_names(session, speakers_table, sessions_speakers_table):

    # use an inner join to get all names corresponding to the session id
    speaker_names = [
        speaker["name"]
        for speaker
        in speakers_table.select(
            columns=["name"],
            join=[(speakers_table, sessions_speakers_table, "id", "speaker_id")],
            where={"session_id":session["id"]}
        )
    ]
    return speaker_names

#
# Session printer
# Prints the following data for a single session:
# {date, time_start, time_end, title, location, description, speakers}
# If the data for any of these fields is missing, "None" will be printed.
# Data is printed line by line between two vertical bars, each composed of 64 equal signs.
#
# \param session         dict<string, string>  dict of columns and values associated with a single session
# \param speaker_names   array<string>         array of speakers associated with the session
#
def print_session(session, speaker_names):
    print("===============================================================")

    for key in DISPLAY_COLUMNS:
        print(f"{key}: {session[key]}\n")

    print(f"speakers: {'; '.join(speaker_names) if speaker_names else "None"}")

    print("===============================================================\n")

#
# Driver Program
# Validates the input query, collects all sessions and speakers that match the query,
# and prints the matches to standard output.
# Any exceptions raised during are caught and logged to the standard output
#
def main():
    try:
        validate_query()

        column = sys.argv[1]
        value = " ".join(sys.argv[2:])

        # accessing tables that have already been created
        sessions_table = db_table("sessions", sessions_schema)
        speakers_table = db_table("speakers", speakers_schema)
        sessions_speakers_table = db_table("sessions_speakers", sessions_speakers_schema)

        # retrieve all sessions that match the query
        all_matched_sessions = get_all_matches(column, value, sessions_table, sessions_speakers_table, speakers_table)

        # retreive all speakers attending each session, and print each session
        for session in all_matched_sessions:
            speaker_names = get_speaker_names(session, speakers_table, sessions_speakers_table)
            print_session(session, speaker_names)

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

