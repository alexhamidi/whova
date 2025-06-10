# Basic function for processing data before and after insertion into the database
#
# Provides small set of utility functions to escape apostrophes
# and trim whitespaces before inserting data to the database, and to
# resubstitute apostrophes before returning data from the database
#


#
# Value processor
# Preprocess the value by substituting apostrophes for double apostrophes
# and trimming leading/trailing whitespaces if it is a string
#
# \param value any        data to be processed
#
# \return any
#
# Example preprocess_value("Keynote: ")
#         preprocess_value(42)
#         preprocess_value("Achilles' Heel")
#
def preprocess_value(value):
    if isinstance(value, str):
        return str(value).replace("'", "''").strip()
    else:
        return value
#
# Value processor
# Postprocesses the value by substituting double apostrophes
# for apostrophes if it is a string.
#
# \param value any        data to be processed
#
# \return any
#
# Example preprocess_value("Keynote:")
#         preprocess_value(42)
#         preprocess_value("Achilles'' Heel")
#
def postprocess_value(value):
    if isinstance(value, str):
        return value.replace("''", "'")
    else:
        return value
