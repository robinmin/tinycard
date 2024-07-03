#!/usr/bin/env python3

import csv
import mysql.connector

# Database connection details (replace with your actual credentials)
HOST = "localhost"
USERNAME = "robin"
PASSWORD = ""
DATABASE = "english"

# CSV file path (replace with your actual file path)
CSV_FILE = "/Users/minlongbing/Projects2/tinycard/data/GPT_Words.csv"
# CSV_FILE = "/Users/minlongbing/Projects2/tinycard/data/GPT_Words2.csv"

# Batch size for inserts
BATCH_SIZE = 100

import csv
import mysql.connector

# Counters
lines_processed = 0
rows_inserted = 0
failed_insertions = 0


def connect_to_db():
    """Connects to the MySQL database.

    Returns:
        A mysql.connector connection object if successful, None otherwise.
    """
    try:
        connection = mysql.connector.connect(
            host=HOST, user=USERNAME, password=PASSWORD, database=DATABASE
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None


def insert_batch(connection, cursor, data):
    """Inserts a batch of data into the table.

    Args:
        connection: The MySQL connection object.
        cursor: A MySQL cursor object.
        data: A list of lists containing the data to insert.
    """
    global rows_inserted, failed_insertions  # Access global counters

    try:
        # Prepare INSERT statement with placeholder values for each field
        insert_query = """INSERT INTO gpt_8k_words (word, analysis, example, etymology, affix, history, word_form, memory_aid, story)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.executemany(insert_query, data)
        connection.commit()
        rows_inserted += len(data)
        print(f"Successfully inserted {len(data)} rows.")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        failed_insertions += len(data)
        # Log failed words for further investigation (optional)
        for row in data:
            print(f"Failed to insert word: {row[0]}")


def main():
    """Main function to handle file processing and database interactions."""
    global lines_processed  # Access global counter

    connection = connect_to_db()
    if not connection:
        return

    try:
        with open(CSV_FILE, "r", encoding="UTF-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            next(reader)  # Skip header row

            data = []
            for row in reader:
                lines_processed += 1
                data.append(row)

                if len(data) == BATCH_SIZE:
                    cursor = connection.cursor()
                    insert_batch(connection, cursor, data)
                    data = []  # Reset batch data

            # Insert any remaining rows after the last batch
            if data:
                cursor = connection.cursor()
                insert_batch(connection, cursor, data)

    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILE}' not found.")
    finally:
        if connection:
            connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    main()

    # Print final counters after script execution
    print(f"\nLines processed: {lines_processed}")
    print(f"Rows inserted: {rows_inserted}")
    print(f"Failed insertions: {failed_insertions}")
