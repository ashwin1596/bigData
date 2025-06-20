"""
Main features of the script include:

Class `FunctionalDependencyDiscovery`:
    - Handles FD discovery for a specific table.
    - Methods:
        - `fetch_data`: Fetches table rows and attributes.
        - `compute_single_attribute_partitions`: Precomputes partitions for efficiency.
        - `check_dependency`: Validates if LHS determines RHS.
        - `discover_dependencies`: Implements the lattice traversal and FD discovery algorithm. -- Several helper functions added to modularize code.
        - `report_dependencies`: Outputs results and prints a summary.
Class `DatabaseConnection`:
    - Manages database connections and cursors.
Main Method:
    - Hardcodes table names and primary keys.
    - Iterates over tables, performing FD discovery for each.

Requirements:
- `psycopg2` library for PostgreSQL connection handling.

HOW TO RUN:
1) EDIT the database credentials in the main method.
2) Modify the hardcoded values for tables as required.
3) Run this File.
4) Get the output in 2 txt files generated.
"""

import psycopg2
from itertools import combinations
from collections import defaultdict

class FunctionalDependencyDiscovery:
    def __init__(self, db_connection, table_name, primary_key):
        self.db_connection = db_connection
        self.table_name = table_name
        self.primary_key = primary_key
        self.attributes = []
        self.rows = []
        self.partitions = {}
        self.tested_dependencies = set()
        self.valid_dependencies = set()
        self.invalid_dependencies = set()
        self.pruned_output_file = "pruned_dependencies.txt"
        self.valid_output_file = "valid_dependencies.txt"

    def fetch_data(self, offset=0, batch_size=1000):
        try:
            query = f"SELECT * FROM {self.table_name} OFFSET {offset} LIMIT {batch_size}"
            self.db_connection.cursor.execute(query)
            rows = self.db_connection.cursor.fetchall()
            if not rows:
                return False
            self.rows = rows
            self.attributes = [desc[0] for desc in self.db_connection.cursor.description]
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

    def compute_single_attribute_partitions(self):
        for idx, attr in enumerate(self.attributes):
            partition = defaultdict(set)
            for row_idx, row in enumerate(self.rows):
                partition[row[idx]].add(row_idx)
            self.partitions[(attr,)] = list(partition.values())

    def compute_partition(self, attrs):
        if attrs in self.partitions:
            return self.partitions[attrs]
        else:
            indices = [self.attributes.index(attr) for attr in attrs]
            partition = defaultdict(set)
            for row_idx, row in enumerate(self.rows):
                key = tuple(row[idx] for idx in indices)
                partition[key].add(row_idx)
            self.partitions[attrs] = list(partition.values())
            return self.partitions[attrs]

    def check_dependency(self, lhs_attrs, rhs_attr):
        lhs_partition = self.compute_partition(lhs_attrs)
        rhs_index = self.attributes.index(rhs_attr)
        for block in lhs_partition:
            rhs_values = set(self.rows[idx][rhs_index] for idx in block)
            if len(rhs_values) > 1:
                return False
        return True

    def discover_dependencies(self):
        lhs_combinations = self.generate_lhs_combinations()
        rhs_attributes = self.get_rhs_candidates()

        with open(self.pruned_output_file, "a") as pruned_file, open(
                self.valid_output_file, "a") as valid_file:
            self.write_table_headers(pruned_file, valid_file)

            for lhs_attrs in lhs_combinations:
                if self.is_trivial_dependency(lhs_attrs):
                    self.write_pruned_dependency(pruned_file, lhs_attrs,
                                                 "primary key is trivial")
                    continue

                for rhs_attr in rhs_attributes:
                    if self.is_rhs_in_lhs(lhs_attrs, rhs_attr):
                        continue

                    dependency = (lhs_attrs, rhs_attr)

                    if dependency in self.tested_dependencies:
                        continue

                    if self.prune_negative_dependencies(lhs_attrs, rhs_attr,
                                                        pruned_file):
                        continue

                    self.test_dependency(dependency, lhs_attrs, rhs_attr,
                                         pruned_file, valid_file)

    def generate_lhs_combinations(self):
        lhs_combinations = []
        for size in range(1, 3):  # Only combinations of size 1 or 2
            lhs_combinations.extend(combinations(self.attributes, size))
        return lhs_combinations

    def get_rhs_candidates(self):
        return [attr for attr in self.attributes if
                attr.lower() not in {'mtatax', 'improvementsurcharge'}]

    def write_table_headers(self, pruned_file, valid_file):
        pruned_file.write(
            f"\n----------- Functional Dependencies for {self.table_name} -----------\n")
        valid_file.write(
            f"\n----------- Functional Dependencies for {self.table_name} -----------\n")

    def is_trivial_dependency(self, lhs_attrs):
        return self.primary_key in lhs_attrs and len(lhs_attrs) > 1

    def write_pruned_dependency(self, pruned_file, lhs_attrs, reason):
        pruned_file.write(
            f"Pruned (trivial): {', '.join(lhs_attrs)} -> {reason}\n")

    def is_rhs_in_lhs(self, lhs_attrs, rhs_attr):
        return rhs_attr in lhs_attrs

    def prune_negative_dependencies(self, lhs_attrs, rhs_attr, pruned_file):
        for i in range(1, len(lhs_attrs)):
            for subset in combinations(lhs_attrs, i):
                if (subset, rhs_attr) in self.invalid_dependencies:
                    pruned_file.write(
                        f"Pruned due to --> (negative result) | The FD: {', '.join(lhs_attrs)} -> {rhs_attr}\n")
                    return True
        return False

    def test_dependency(self, dependency, lhs_attrs, rhs_attr, pruned_file,
                        valid_file):
        self.tested_dependencies.add(dependency)
        if self.check_dependency(lhs_attrs, rhs_attr):
            self.valid_dependencies.add(dependency)
            valid_file.write(f"{', '.join(lhs_attrs)} -> {rhs_attr}\n")
        else:
            self.invalid_dependencies.add(dependency)
            pruned_file.write(
                f"Pruned due to --> (invalid): {', '.join(lhs_attrs)} -> {rhs_attr}\n")

    def report_dependencies(self):
        print(f"Pruned dependencies updated in  {self.pruned_output_file}.")
        print(f"Valid dependencies updated in {self.valid_output_file}.")

# Connect to PostgreSQL
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

# Main Execution
if __name__ == "__main__":
    db_conn = DatabaseConnection(
        database="project",
        user="postgres",
        password="RIT@2023",
        host="localhost",
        port="5432"
    )

    # File paths for storing combined dependencies
    pruned_output_file = "pruned_dependencies.txt"
    valid_output_file = "valid_dependencies.txt"

    # Clear the files at the start
    with open(pruned_output_file, "w") as pruned_file, open(valid_output_file, "w") as valid_file:
        pruned_file.write("Pruned Functional Dependencies\n")
        valid_file.write("Valid Functional Dependencies\n")

    try:
        db_conn.connect()

        # Hardcoded table names and their primary keys
        tables = [
            {"name": "Location", "primary_key": "ID"},
            {"name": "RateCode", "primary_key": "ID"},
            {"name": "Payment", "primary_key": "ID"},
            {"name": "Vendor", "primary_key": "ID"},
            {"name": "Trip", "primary_key": "ID"}
        ]

        for table in tables:
            table_name = table["name"]
            primary_key = table["primary_key"]

            print(f"Discovering FDs for table: {table_name}")
            print("-" * 40)

            # Create an instance for FD discovery
            fd_discovery = FunctionalDependencyDiscovery(db_conn, table_name, primary_key)

            # Fetch data and compute FDs
            fd_discovery.fetch_data()
            fd_discovery.compute_single_attribute_partitions()
            fd_discovery.discover_dependencies()

            # Reporting is now handled in `discover_dependencies`
            fd_discovery.report_dependencies()
            print("-" * 40)

    finally:
        db_conn.disconnect()