import psycopg2 as pg
from contextlib import contextmanager

conn_params1 = {
    'dbname': 'project_v1',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

conn_params2 = {
    'dbname': 'project_v3',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}


@contextmanager
def get_connection(conn_params):
    """Context manager for database connections"""
    conn = None
    try:
        conn = pg.connect(**conn_params)
        yield conn
    except pg.Error as e:
        print(f"Database connection error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


def create_table():
    try:
        with get_connection(conn_params2) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS trip(
                        passengercount VARCHAR(10),
                        tripdistance VARCHAR(10),
                        ratecodeid INTEGER,
                        storeandfwdflag CHAR(1),
                        paymenttype INTEGER,
                        fareamount VARCHAR(20),
                        tipamount VARCHAR(20),
                        tollsamount VARCHAR(20),
                        totalamount VARCHAR(20),
                        pulocationid INTEGER,
                        dolocationid INTEGER
                    )
                ''')
                conn.commit()
    except pg.Error as e:
        print(f"Error creating table: {e}")
        raise


def bin_numeric_value(value, bins):
    """Generic function to bin numeric values"""
    for bin_name, (lower, upper) in bins.items():
        if lower <= value < upper:
            return bin_name
    return 'other'


def insert_data():
    try:
        # Fetch data from source database
        with get_connection(conn_params1) as source_conn:
            with source_conn.cursor() as source_cur:
                source_cur.execute('SELECT * FROM trip')
                rows = source_cur.fetchall()

        # Prepare binning configurations
        passenger_bins = {
            '<6': (0, 6),
            '6+': (6, float('inf'))
        }

        trip_distance_bins = {
            '<1': (0, 1),
            '1-5': (1, 5),
            '5-10': (5, 10),
            '10+': (10, float('inf'))
        }

        fare_bins = {
            '<100': (0, 100),
            '100-500': (100, 500),
            '500-1000': (500, 1000),
            '1000+': (1000, float('inf'))
        }

        tip_bins = {
            '0': (0, 0),
            '<50': (0, 50),
            '50-100': (50, 100),
            '100+': (100, float('inf'))
        }

        tolls_bins = {
            '<50': (0, 50),
            '50-100': (50, 100),
            '100+': (100, float('inf'))
        }

        total_bins = {
            '<100': (0, 100),
            '100-500': (100, 500),
            '500-1000': (500, 1000),
            '1000+': (1000, float('inf'))
        }

        # Insert processed data
        with get_connection(conn_params2) as dest_conn:
            with dest_conn.cursor() as dest_cur:
                processed_data = []
                for row in rows:
                    processed_row = (
                        str(bin_numeric_value(row[1], passenger_bins)),
                        str(bin_numeric_value(row[2], trip_distance_bins)),
                        int(row[15]),
                        str(row[3]),
                        int(row[14]),
                        str(bin_numeric_value(row[4], fare_bins)),
                        str(bin_numeric_value(row[8], tip_bins)),
                        str(bin_numeric_value(row[9], tolls_bins)),
                        str(bin_numeric_value(row[10], total_bins)),
                        int(row[16]),
                        int(row[17])
                    )
                    processed_data.append(processed_row)

                # Batch insert with error handling
                dest_cur.executemany('''
                    INSERT INTO trip(
                     passengercount,
                    tripdistance,
                    ratecodeid,
                    storeandfwdflag,
                    paymenttype,
                    fareamount,
                    tipamount,
                    tollsamount,
                    totalamount,
                    pulocationid,
                    dolocationid) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', processed_data)
                dest_conn.commit()

    except pg.Error as e:
        print(f"Database insertion error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def prepend_col_tag(data, col_idx):
    if col_idx == 0:
        return f'passengercount:{data}'
    elif col_idx == 1:
        return f'tripdistance:{data}'
    elif col_idx == 2:
        return f'ratecodeid:{data}'
    elif col_idx == 3:
        return f'storeandfwdflag:{data}'
    elif col_idx == 4:
        return f'paymenttype:{data}'
    elif col_idx == 5:
        return f'fareamount:{data}'
    elif col_idx == 6:
        return f'tipamount:{data}'
    elif col_idx == 7:
        return f'tollsamount:{data}'
    elif col_idx == 8:
        return f'totalamount:{data}'
    elif col_idx == 9:
        return f'pulocationid:{data}'
    elif col_idx == 10:
        return f'dolocationid:{data}'


def prepareItems():
    try:
        with get_connection(conn_params2) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT * FROM trip
                ''')
                rows = cur.fetchall()

                cur.execute('''
                                    CREATE TABLE IF NOT EXISTS items(
                                        tid INTEGER,    
                                        item varchar
                                    )
                            ''')
                conn.commit()

                processed_data = []

                tid = 1

                for row in rows:
                    current_items = []
                    for i in range(0, len(row)):
                        current_items.append((tid, prepend_col_tag(row[i], i)))
                    processed_data.extend(current_items)

                    tid += 1

                    if tid % 1000000 == 0:
                        cur.executemany('''
                            INSERT INTO items(tid, item) VALUES (%s, %s)
                        ''', processed_data)
                        conn.commit()
                        processed_data = []

                if processed_data:
                    cur.executemany('''
                        INSERT INTO items(tid, item) VALUES (%s, %s)
                    ''', processed_data)
                    conn.commit()

    except pg.Error as e:
        print(f"Error preparing items: {e}")
        raise


def main():
    create_table()
    insert_data()
    prepareItems()


if __name__ == '__main__':
    main()
