"""
Script Overview:
This script is designed to handle functional dependency (FD) discovery for
relational database tables and perform data cleaning tasks.
It includes utility classes for managing database connections and automating FD discovery.

Main Features:

1. Class `DatabaseConnection`:
   - Provides a wrapper for PostgreSQL connection management.
   - Includes methods to:
       - `connect`: Establish a database connection.
       - `disconnect`: Close the database connection and cursor.
       - `drop_constraints`: Temporarily drop foreign key constraints for cleaning.
       - `reapply_constraints`: Reinstate foreign key constraints with `ON DELETE CASCADE` as needed.
       - `clean_data`: Executes cleaning queries, logging affected rows.

3. Main Method:
   - Connects to the database using the `DatabaseConnection` class.
   - Drops foreign key constraints temporarily for data cleaning.
   - Executes a series of cleaning queries to remove invalid or redundant rows.
   - Outputs the total number of rows deleted across all queries.
   - Ensures reconnection or rollback in case of errors.

Requirements:
psycopg2: Used for PostgreSQL database interaction.

HOW TO RUN:
1. Update database credentials in the `main` method (e.g., `database`, `user`, `password`).
2. Modify or add hardcoded table names and queries in the `cleaning_queries` list as needed.
3. Execute this script from the command line
   """

import psycopg2
class DatabaseConnection:
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database")
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Disconnected from the database")

    def drop_constraints(self):
        try:
            print("Dropping foreign key constraints...")

            # Drop the constraints temporarily
            self.cursor.execute("""
                ALTER TABLE public.Time DROP CONSTRAINT IF EXISTS fk_tripid;
                ALTER TABLE public.Trip DROP CONSTRAINT IF EXISTS fk_pickup_location;
                ALTER TABLE public.Trip DROP CONSTRAINT IF EXISTS fk_dropoff_location;
            """)

            # Commit changes to ensure constraints are dropped
            self.connection.commit()
            print("Constraints dropped successfully.")
        except psycopg2.Error as e:
            print(f"Error dropping constraints: {e}")
            self.connection.rollback()

    def reapply_constraints(self):
        try:
            print("Reapplying foreign key constraints...")
            # Reapply the constraints with ON DELETE CASCADE
            self.cursor.execute("""
                ALTER TABLE public.Time
                ADD CONSTRAINT fk_tripid
                FOREIGN KEY (TripID)
                REFERENCES public.Trip (ID)
                ON DELETE CASCADE;

                ALTER TABLE public.Trip
                ADD CONSTRAINT fk_pickup_location
                FOREIGN KEY (PickUpLocation)
                REFERENCES public.Location (ID)
                ON DELETE CASCADE;

                ALTER TABLE public.Trip
                ADD CONSTRAINT fk_dropoff_location
                FOREIGN KEY (DropOffLocation)
                REFERENCES public.Location (ID)
                ON DELETE CASCADE;
            """)
            self.connection.commit()
            print("Constraints reapplied successfully.")
        except psycopg2.Error as e:
            print(f"Error reapplying constraints: {e}")
            self.connection.rollback()

    def clean_data(self, query, description):
        try:
            print(f"Executing cleaning query: {description}")
            self.cursor.execute(query)

            # Log the number of rows affected
            rows_deleted = self.cursor.rowcount
            print(f"Rows deleted for query '{description}': {rows_deleted}")

            # Commit c
            self.connection.commit()
            return rows_deleted

        except psycopg2.Error as e:
            print(f"Error during data cleaning for query '{description}': {e}")
            self.connection.rollback()
            raise e

def main():
    db_conn = DatabaseConnection(
        database="project",
        user="postgres",
        password="RIT@2023",
        host="localhost",
        port="5432"
    )
    try:
        db_conn.connect()


        db_conn.drop_constraints()

        cleaning_queries = [
            {
                "query": """
                        DELETE FROM public.Location
                        WHERE Borough IS NULL OR Zone IS NULL;
                    """,
                "description": "Remove rows with NULL Borough or Zone from Location table"
            },
            {
                "query": """
                        DELETE FROM public.Location
                        WHERE (Borough, Zone) IN (
                            SELECT Borough, Zone
                            FROM public.Location
                            GROUP BY Borough, Zone
                            HAVING COUNT(*) > 1
                        );
                    """,
                "description": "Remove duplicate Borough and Zone combinations from Location table"
            },
            {
                "query": """
                        DELETE FROM public.Time
                        WHERE DropOffDate < PickUpDate
                        OR (DropOffDate = PickUpDate AND DropOffTime < PickUpTime);
                    """,
                "description": "Remove rows with invalid DropOffDate/DropOffTime from Time table"
            },
            {
                "query": """
                        DELETE FROM public.Trip
                        WHERE PassengerCount < 1
                        OR TripDistance < 0
                        OR FareAmount < 0;
                    """,
                "description": "Remove rows with invalid PassengerCount, TripDistance, or FareAmount from Trip table"
            }
        ]

        total_deleted = 0


        for item in cleaning_queries:
            try:
                rows_deleted = db_conn.clean_data(item["query"],
                                                  item["description"])
                total_deleted += rows_deleted
            except psycopg2.Error:
                print("An error occurred. Rolling back changes.")
                break

        print(
            f"Total rows deleted across all successfully executed queries: {total_deleted}")

    finally:
        db_conn.disconnect()


if __name__ == "__main__":
    main()


