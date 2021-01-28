import psycopg2
import psycopg2.extras



DB_HOST = "localhost"
DB_NAME = "tikus_events"
DB_USER = "postgres"
DB_PASS = "123456"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

with conn:
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        
        # cur.execute("CREATE TABLE IF NOT EXISTS user_info ( user_id serial PRIMARY KEY, username VARCHAR ( 50 ) UNIQUE NOT NULL, password VARCHAR ( 50 ) NOT NULL,email VARCHAR ( 255 ) UNIQUE NOT NULL,created_on TIMESTAMP NOT NULL,profile_url VARCHAR ( 250 ), followers INT );")
        

conn.commit()

cur.close()

conn.close()