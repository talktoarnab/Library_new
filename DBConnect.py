import mysql.connector

# Establish a connection to the MySQL server
mydb = mysql.connector.connect(
    host="db-lib1.czkmy4iscxhb.us-east-1.rds.amazonaws.com",     # Your host, usually 'localhost'
    user="arnab",          # Your username
    password="arnabdas",
    port="3306", # Your password
    database="Library"       # Your database name
)

# Check if the connection is successful
if mydb.is_connected():
    print('Connected to MySQL database')

    # Perform a query
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Book")

    # Fetch all rows from the query
    rows = mycursor.fetchall()

    # Display the rows
    for row in rows:
        print(row)

    # Close cursor and connection
    mycursor.close()
    mydb.close()
    print('MySQL connection closed')

else:
    print('Connection to MySQL database failed')