#src/models/__init__.py

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# initialize our db
db = SQLAlchemy()
ma = Marshmallow()

from .note import NoteModel, NoteSchema