# util functions for serialization/deserialization
from utils import preprocess_value, postprocess_value

# sqlite db communication
import sqlite3

# Very basic SQLite wrapper
#
# Creates table from schema
# Provides small set of utility functions to query the database
#
# If you need to change the schema of an already created table, reset the database
# If you need to reset the database, just delete the database file (db_table.DB_NAME)
#
class db_table:


    # SQLite database filename
    DB_NAME = "interview_test.db"



    #
    # model initialization
    # records table name and schema
    # creates the table if it does not exist yet in DB
    #
    # \param name    string                name of the DB table
    # \param schema  dict<dict<string, string>, array<string>>  schema of DB table, with a column dict mapping column names to their DB type and a constraint array with constraints to apply to the table
    #
    # Example: table("users", { "columns": {"id": "integer PRIMARY KEY", "name": "text", "manager_id": "integer"}, "constraints": ["FOREIGN KEY(manager_id) REFERENCES users(id)"]})
    #
    def __init__(self, name, schema):
        # error handling
        if not name:
            raise RuntimeError("invalid table name")
        if not schema:
            raise RuntimeError("invalid database schema")

        # init fields and initiate database connection
        self.name         = name
        self.columns      = schema["columns"]
        self.constraints  = schema["constraints"]
        self.db_conn      = sqlite3.connect(self.DB_NAME)

        # ensure the table is created
        self.create_table()

    #
    # CREATE TABLE IF NOT EXISTS wrapper
    # Create the database table based on self.name and self.schema
    # If table already exists, nothing is done even if the schema has changed
    # If you need to apply schema changes, please delete the database file
    #
    def create_table(self):
        # { "columns": { "id": "integer", "name": "text" }, "constraints":["CHECK(age >= 18)"] } -> "id integer, name text, CHECK(age >=18)"
        columns_query_string  = ', '.join([ "%s %s" % (k,v) for k,v in self.columns.items() ] + self.constraints)

        # CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, name text)
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        self.db_conn.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (self.name, columns_query_string))
        self.db_conn.commit()

    #
    # SELECT wrapper
    # Query the database by applying the specified filters
    #
    # \param columns  array<string>         columns to be fetched. if empty, will query all the columns
    # \param join  array<tuple<db_table, db_table, string, string>>     tables and columns of a join query.  Each tuple represents a join condition with the following structure: (table1, table2, table1_column, table2_column). The join is made with the condition "JOIN table_2 ON table1.table1_column = table2.table2_column"
    # \param where   dict<string, string | list<string>>  where filters to be applied. The keys are column names, and the values are either A single value to filter for strict equality or list of values for an IN clause. Only AND is used to combine conditions.
    #
    # \return [ { col1: val1, col2: val2, col3: val3 } ]
    #
    # Example table.select(["name"], { "id": "42" })
    #         table.select()
    #         table.select(where={ "name": "John" })
    #         table.select(["name"], { "id": ["42", "32"]})
    #
    def select(self, columns = [], join = [], where = {}):
        # by default, query all columns
        if not columns:
            columns = [ k for k in self.columns ]

        # build query string
        columns_query_string = ", ".join(columns)
        query                = "SELECT %s.%s FROM %s" % (self.name, columns_query_string, self.name)

        # build join query string
        if join:
            join_query_string = ["%s ON %s.%s = %s.%s" % (table2.name, table1.name, table1_column, table2.name, table2_column)
                                for table1, table2, table1_column, table2_column in join]
            query += " JOIN " + " JOIN ".join(join_query_string)

        # build where query string
        if where:
            where_query_string = [ ("%s IN (%s)" % (k, ", ".join([str(preprocess_value(val)) for val in v]))) if isinstance(v, list) else
                                   ("%s = '%s'"  % (k, preprocess_value(v))) for k, v in where.items()]
            query += " WHERE " + ' AND '.join(where_query_string)



        result = []
        # SELECT id, name FROM users [ WHERE id=42 AND name=John ]
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        for row in self.db_conn.execute(query):
            result_row = {}
            # convert from (val1, val2, val3) to { col1: val1, col2: val2, col3: val3 }
            for i in range(0, len(columns)):
                value = row[i]
                result_row[columns[i]] = postprocess_value(value)
            result.append(result_row)
        return result

    #
    # INSERT INTO wrapper
    # insert the given item into database
    #
    # \param item  dict<string, string>   item to be insert in DB, mapping column to value
    #
    # \return id of the created record
    #
    # Example table.insert({ "id": "42", "name": "John" })
    #
    def insert(self, item):
        # build columns & values queries

        columns_query = ", ".join(item.keys())
        values_query  = ", ".join([ "'%s'" % preprocess_value(v) for v in item.values()])



        #print(len(item.values()))
        #print(item["Speakers"])
        # INSERT INTO users(id, name) values (42, John)
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO %s (%s) VALUES (%s)" % (self.name, columns_query, values_query))
        cursor.close()
        self.db_conn.commit()
        return cursor.lastrowid

    #
    # UPDATE wrapper
    # update multiple rows matching the specified condition
    #
    # \param values  dict<string, string>  values to be updates, mapping column to value
    # \param where   dict<string, string>  where filters to be applied. only combine them using AND and only check for strict equality
    #
    # \return number of updated records
    #
    # Example table.update({ "name": "Simon" }, { "id": 42 })
    #
    def update(self, values, where):
        # build set & where queries
        set_query   = ", ".join(["%s = '%s'" % (k, preprocess_value(v)) for k,v in values.items()])
        where_query = " AND ".join(["%s = '%s'" % (k, preprocess_value(v)) for k,v in where.items()])

        # UPDATE users SET name = Simon WHERE id = 42
        #
        # Note that columns are formatted into the string without using sqlite safe substitution mechanism
        # The reason is that sqlite does not provide substitution mechanism for columns parameters
        # In the context of this project, this is fine (no risk of user malicious input)
        cursor = self.db_conn.cursor()
        cursor.execute("UPDATE %s SET %s WHERE %s" % (self.name, set_query, where_query))
        cursor.close()
        self.db_conn.commit()
        return cursor.rowcount

    #
    # Close the database connection
    #
    def close(self):
        self.db_conn.close()



