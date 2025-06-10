# Schema Definitons
#
# Defines the database schema for each table in the database.
# They include columns, data types, and any constraints like primary keys and foreign keys.
#

#
# Sessions schema
# This schema defines the structure of the 'sessions' table, including column data types
# and constraints such as the foreign key linking to a subsession's supersessions.
#
sessions_schema = {
    "columns":{
        "id":"INTEGER PRIMARY KEY AUTOINCREMENT",
        "date":"VARCHAR(10)",
        "time_start":"VARCHAR(8)",
        "time_end":"VARCHAR(8)",
        "title":"VARCHAR(255)",
        "location":"VARCHAR(255)",
        "description":"TEXT",
        "supersession_id":"INTEGER",
    },
    "constraints": [
        "FOREIGN KEY (supersession_id) REFERENCES sessions(id)"
    ]
}

#
# Sessions speakers schema
# This schema defines the structure of the 'sessions_speakers' table, a join
# table that is used to represent the many-to-many relationships between sessions
# and speakers
#
sessions_speakers_schema = {
    "columns":{
        "session_id": "INTEGER",
        "speaker_id": "INTEGER",
    },
    "constraints":[
        "PRIMARY KEY (session_id, speaker_id)",
        "FOREIGN KEY (session_id) REFERENCES sessions(id)",
        "FOREIGN KEY (speaker_id) REFERENCES speakers(id)"
    ]
}

#
# Speakers schema
# This schema defines the structure of the 'speakers' table. The name of each speaker in
# this table must be unique.
#
speakers_schema = {
    "columns":{
        "id":"INTEGER PRIMARY KEY AUTOINCREMENT",
        "name":"VARCHAR(255) UNIQUE",
    },
    "constraints":[]
}
