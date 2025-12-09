from flask import Flask
from database import init_db, create_tables

app = Flask(__name__)
init_db(app)
create_tables(app)

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
