import sqlite3


def print_market_data():
    # Connect to the SQLite database
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()

    # SQL query to select all data from market_data table
    query = "SELECT * FROM market_data"

    try:
        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        # Print the results
        for row in results:
            print(f"ID: {row[0]}, Exchange: {row[1]}, Timestamp: {row[2]}, "
                  f"Event Number: {row[3]}, Liquidations: {row[4]}, "
                  f"Large Trades: {row[5]}, Open Price: {row[6]}, "
                  f"Close Price: {row[7]}, High Price: {row[8]}, "
                  f"Low Price: {row[9]}, Base Asset Volume: {row[10]}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the database connection
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print_market_data()
