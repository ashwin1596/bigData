import psycopg2 as pg

conn_params = {
    'dbname': 'project_v3',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}


class AprioriLattice:
    def __init__(self, db_connection, min_support=100):
        """
        Initialize the Apriori algorithm implementation
        :param db_connection: connection object to the database
        :param min_support: minimum support threshold for frequent itemsets
        """
        self.conn = db_connection
        self.min_support = min_support
        self.frequent_item_sets = {}

    def generate_l1(self):
        """
        Generate level 1 frequent itemsets
        :return: True if item count > 0, False otherwise
        """
        cursor = self.conn.cursor()

        # Create L1 table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS L1 AS
            SELECT item as item1, COUNT(*) as count
            FROM items
            GROUP BY item
            HAVING COUNT(*) >= %s;
        """, (self.min_support,))

        # Check if L1 table is empty
        cursor.execute("SELECT COUNT(*) FROM L1;")
        count = cursor.fetchone()[0]
        self.frequent_item_sets[1] = count

        self.conn.commit()
        return count > 0

    def generate_next_level(self, current_level):
        """
        Generate the next level of frequent itemsets
        :param current_level: integer representing the current level (k)
        :return: boolean indicating if any frequent itemsets were found
        """
        cursor = self.conn.cursor()

        # Generate join condition and column lists for the candidate generation
        join_conditions = []
        select_columns = []

        # for L2 and above, we need to join the previous level with itself
        for i in range(1, current_level - 1):
            join_conditions.append(f"p.item{i} = q.item{i}")
            select_columns.append(f"p.item{i}")

        # Add the last two columns and condition
        select_columns.extend([
            f"p.item{current_level - 1}",
            f"q.item{current_level - 1} as item{current_level}"
        ])
        join_conditions.append(
            f"p.item{current_level - 1} < q.item{current_level - 1}"
        )

        # Generate the table names
        candidate_table = f"C{current_level}"
        result_table = f"L{current_level}"

        # Create the candidate table
        candidate_query = f"""
            CREATE TABLE {candidate_table} AS
            SELECT {','.join(select_columns)}
            FROM L{current_level - 1} p, L{current_level - 1} q
            WHERE {' AND '.join(join_conditions)};
        """

        cursor.execute(candidate_query)

        # Generate items joins and conditions for counting
        item_joins = []
        item_conditions = []
        for i in range(1, current_level + 1):
            item_joins.append(
                f"INNER JOIN items pt{i} ON c.item{i} = pt{i}.item"
            )
            if i > 1:
                item_conditions.append(
                    f"pt1.tid = pt{i}.tid"
                )

        # Count frequent itemsets
        count_query = f"""
        CREATE TABLE IF NOT EXISTS {result_table} AS
        SELECT c.*, COUNT(*) as count
        FROM {candidate_table} c
        {' '.join(item_joins)}
        WHERE {' AND '.join(item_conditions)}
        GROUP BY {', '.join(f'c.item{i}' for i in range(1, current_level + 1))}
        HAVING COUNT(*) >= %s;
        """
        cursor.execute(count_query, (self.min_support,))

        # Check if we found any frequent itemsets at this level
        cursor.execute(f"SELECT COUNT(*) FROM {result_table};")
        count = cursor.fetchone()[0]
        if count > 0:
            self.frequent_item_sets[current_level] = count

        # Clean up temporary table
        cursor.execute(f"DROP TABLE {candidate_table};")

        self.conn.commit()
        return count > 0

    def generate_all_levels(self):
        """
        Generate all levels of the intemset lattice until no more frequent itemsets are found

        :return: Number of levels generated
        """
        # Generate L1
        if not self.generate_l1():
            return 0

        print("Generated L1")

        current_level = 2

        # Keep generating levels until we find no more frequent itemsets
        while self.generate_next_level(current_level):
            current_level += 1
            print(f"Generated L{current_level - 1}")

        return current_level


def main():
    # Connect to the database
    conn = pg.connect(**conn_params)

    # Create the AprioriLattice object
    apriori = AprioriLattice(conn, min_support=1000)

    # Generate all levels of the itemset lattice
    apriori.generate_all_levels()
    num_levels = len(apriori.frequent_item_sets)
    print(f"Generated {num_levels} levels of the itemset lattice")

    conn.close()


if __name__ == '__main__':
    main()
