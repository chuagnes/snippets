import logging, argparse, psycopg2 #psycopg allows you to access psql from python

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")

def put(name, snippet, hidden = False):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet {!r}: {!r}, hidden flag = {!r}".format(name, snippet, hidden))
    with connection, connection.cursor() as cursor:
        try:
            command = "insert into snippets values (%s, %s, %s)"
            cursor.execute(command, (name, snippet, hidden))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s, hidden=%s where keyword=%s"
            cursor.execute(command, (name, snippet, hidden))
    logging.debug("Snippet stored successfully.")
    return name, snippet, hidden

def get(name):
    """Retrieve the snippet with a given name."""
    logging.info("Retrieving snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully.")
    if not row:
        return "404: Snippet Not Found"
    return row[0]

def catalog():
    """Display all of the keywords in the snippets table"""
    logging.info("Displaying all of keywords in the Snippets table.")
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets order by keyword asc")
        list = cursor.fetchall()
    logging.debug("Displayed all keywords in snippets table")
    return list 

def search(string):
    """search the snippet for a given string."""
    logging.info("Searching for string {!r}".format(string))
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where message like %s and not hidden", ('%{}%'.format(string),))
        list = cursor.fetchall()
    logging.debug("Keyword and Snippet retrieved successfully.")
    if not list:
        return "404: String not found"
    return string, list

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet texpt")
    put_parser.add_argument("--hide", dest = "hidden", help="hides snippet", action="store_true")
    put_parser.add_argument("--show", dest = "hidden", help="shows snippet", action="store_false")

    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    # Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Display all keywords in snippets table")
    
    # Subparserfor the search command
    logging.debug("Constructing the search subparser")
    search_parser = subparsers.add_parser("search", help="Search for string")
    search_parser.add_argument("string", help="String that being searched for")

    arguments = parser.parse_args()
    
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments) #vars is built-in function that converts from namespace obj to dict
    command = arguments.pop("command")

    if command == "put":
        name, snippet, hidden = put(**arguments) #** means unpacking, converting k, v pair in dict as function arguments
        print("Stored {!r} as {!r}, hidden flag = {!r}".format(snippet, name, hidden))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        keywords = catalog()
        print("Displaying all keywords in snippet table: {!r}".format(keywords))
    elif command == "search":
        string, listing = search(**arguments)
        print("Found string {!r} in the following entry: {!r}".format(string, listing))

            

    
if __name__ == "__main__":
    main()