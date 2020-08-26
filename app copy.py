import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = 'Expected environmecatnt variable {} not set.'.format(name)
        raise Exception(message)

# the values of those depend on your setup
POSTGRES_URL = get_env_variable('POSTGRES_URL')
POSTGRES_USER = get_env_variable('POSTGRES_USER')
POSTGRES_PW = get_env_variable('POSTGRES_PW')
POSTGRES_DB = get_env_variable('POSTGRES_DB')

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

db = SQLAlchemy(app)
ma = Marshmallow(app)

class NoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(255))

    def __init__(self, title, content):
        self.title = title
        self.content = content


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NoteModel

note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/note/')
def note_list():
    all_notes = NoteModel.query.all()
    return jsonify(notes_schema.dump(all_notes))


@app.route('/note/', methods=['POST'])
def create_note():
    title = request.json.get('title', '')
    content = request.json.get('content', '')

    note = NoteModel(title=title, content=content)
    
    db.session.add(note)
    db.session.commit()
    
    return note_schema.jsonify(note)


@app.route('/note/<int:note_id>/', methods=["GET"])
def note_detail(note_id):
    note = NoteModel.query.get(note_id)
    return note_schema.jsonify(note)


if __name__ == '__main__':
    app.run(debug=True)
