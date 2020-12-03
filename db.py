import sqlite3
from sqlite3 import Error

# Formatting helper functions
def views_str_to_int(s):
    """Input Examples: 
        '100 viewers', '100,000 viewers', '100K viewers' '82.4K viewers'"""
    figure = s.split('viewers')[0]
    if 'K' in figure:
        figure = figure.split('K')[0]
        return int(float(figure)*1000)
    else:
        return int(figure.replace(',', ''))
    
def url_to_id(s, index):
    return s.split('/')[index]

# SQL Statements
# Create tables
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
sql_create_channels_table = """
CREATE TABLE IF NOT EXISTS channels (
    id text PRIMARY KEY,
    name text NOT NULL
); """
sql_create_stream_table = """
CREATE TABLE IF NOT EXISTS streams (
    id integer PRIMARY KEY AUTOINCREMENT,
    seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    viewers int NOT NULL,
    cat_id text,
    channel_id text,
    FOREIGN KEY (cat_id) REFERENCES CATEGORIES (id)
    FOREIGN KEY (channel_id) REFERENCES CHANNELS (id)
); """

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

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)
    return conn

# Insert methods
def insert_category(conn, url, title):
    category = (url_to_id(url, -1), title)
    sql = ''' INSERT OR IGNORE INTO categories(id,title)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, category)
    conn.commit()
def insert_cat_occurrence(conn, url, viewers):
    occ = (views_str_to_int(viewers), url_to_id(url, -1))
    sql = ''' INSERT OR IGNORE INTO cat_occurrences(viewers, cat_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, occ)
    conn.commit()
def insert_channel(conn, channel_url, channel_name):
    channel = (url_to_id(channel_url, -2), channel_name)
    sql = ''' INSERT OR IGNORE INTO channels(id,name)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, channel)
    conn.commit()
def insert_stream(conn, channel_url, cat_url, viewers):
    stream = (views_str_to_int(viewers), url_to_id(cat_url, -1), url_to_id(channel_url, -2))
    sql = ''' INSERT OR IGNORE INTO streams(viewers,cat_id,channel_id)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, stream)
    conn.commit()

if __name__ == "__main__":
    conn = create_connection('example.db')
    # create tables
    if conn is not None:
        # create categories table
        create_table(conn, sql_create_categories_table)

        # create cat_occurrences table
        create_table(conn, sql_create_cat_occurrences_table)

        # create channels table
        create_table(conn, sql_create_channels_table)

        # create streams table
        create_table(conn, sql_create_stream_table)
