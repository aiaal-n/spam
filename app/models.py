from app import app, db
import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator
app.config['SECRET_KEY'] = 'super-secret'


SIZE = 256

class TextPickleType(TypeDecorator):

    impl = sqlalchemy.Text(SIZE)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Mails(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	mails = db.Column(TextPickleType())

	def __init__(self, mails):
		self.mails = mails

db.create_all()