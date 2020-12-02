import sqlite3
from sqlite3 import Error

def views_str_to_int(s):
    figure = s.split('viewers')[0]
    return int(figure.replace(',', ''))

def url_to_id(s):
    return s.split('/')[-1]

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

sql_create_categories_table = """
CREATE TABLE IF NOT EXISTS categories (
    id text PRIMARY KEY,
    title text NOT NULL
); """
sql_create_cat_occurrences_table = """
CREATE TABLE IF NOT EXISTS cat_occurrences (
    id integer PRIMARY KEY AUTOINCREMENT,
    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewers int NOT NULL,
    cat_id text,
    FOREIGN KEY (cat_id) REFERENCES CATEGORIES (id)
); """

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)
    return conn

def insert_category(conn, url, title):
    category = (url_to_id(url), title)
    sql = ''' INSERT OR IGNORE INTO categories(id,title)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, category)
    conn.commit()

def insert_cat_occurrence(conn, url, viewers):
    occ = (views_str_to_int(viewers), url_to_id(url))
    sql = ''' INSERT OR IGNORE INTO cat_occurrences(viewers, cat_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, occ)
    conn.commit()

if __name__ == "__main__":
    conn = create_connection('example.db')
    # create tables
    if conn is not None:
        # create categories table
        create_table(conn, sql_create_categories_table)

        # create cat_occurrences table
        create_table(conn, sql_create_cat_occurrences_table)
