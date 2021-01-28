DB_HOST = "localhost"
DB_NAME = "tikus_events"
DB_USER = "postgres"
DB_PASS = "123456"

import psycopg2
import psycopg2.extras

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# cur.execute("CREATE TABLE user_info (uid SERIAL PRIMARY KEY, user_name VARCHAR, email VARCHAR, pwd VARCHAR, created );")

# cur.execute("INSERT INTO student (name) VALUES(%s)", ("Halid",))
# cur.execute("SELECT * FROM student;")
# print(cur.fetchall())

with conn:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        
        # cur.execute("CREATE TABLE IF NOT EXISTS user_info ( user_id serial PRIMARY KEY, username VARCHAR ( 50 ) UNIQUE NOT NULL, password VARCHAR ( 50 ) NOT NULL,email VARCHAR ( 255 ) UNIQUE NOT NULL,created_on TIMESTAMP NOT NULL,profile_url VARCHAR ( 250 ), followers INT );")
        # cur.execute("CREATE TABLE IF NOT EXISTS event_info ( event_id serial PRIMARY KEY, user_id VARCHAR ( 50 ) UNIQUE NOT NULL, password VARCHAR ( 50 ) NOT NULL,email VARCHAR ( 255 ) UNIQUE NOT NULL,created_on TIMESTAMP NOT NULL,profile_url VARCHAR ( 250 ), followers INT );")
        # print(cur.fetchone()['name'])
        
        # cur.execute("SELECT * FROM student;")
        # print(cur.fetchall())
        

conn.commit()

cur.close()

conn.close()