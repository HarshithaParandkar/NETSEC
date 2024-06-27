import pymssql

def connect_to_database(host, user, password, database):
    try:
        connection = pymssql.connect(
            server=host,
            user=user,
            password=password,
            database=database
        )
        print("Connected to the database successfully.")
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def execute_query(connection, sql_query, params=None):
    try:
        with connection.cursor(as_dict=True) as cursor:
            cursor.execute(sql_query, params)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def execute_non_query(connection, sql_query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query, params)
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        print(f"Error executing non-query: {e}")
        connection.rollback()
        return None
