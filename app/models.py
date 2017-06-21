from app import app, db
app.config['SECRET_KEY'] = 'super-secret'

class Mails(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.Text())
	mails = db.Column(db.Text())

	def __init__(self, name, mails):
		self.name = name
		self.mails = mails

db.create_all()