import psycopg2
import psycopg2.extras
from flask import Flask, request


DB_URL = "postgres://xuijhtqmoyikzo:15b8cb464e2fad66693e89dcb4d8e8b8b93b789281259de9a822399a536a42a4@ec2-54-159-113-254.compute-1.amazonaws.com:5432/dt563jahevl50"

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'


@app.route('/hello')
def hello():
    return 'Hello, There!'


if __name__ == '__main__':
    app.debug = True
    app.run()