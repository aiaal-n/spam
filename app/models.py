from app import app, db

app.config['SECRET_KEY'] = 'super-secret'


class Mails(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    mails = db.Column(db.Text())

    def __init__(self, name, mails):
        self.name = name
        self.mails = mails


class TemplateMessage(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500))
    message = db.Column(db.Text())
    file = db.Column(db.String(500))

    def __init__(self, name, message, file):
        self.name = name,
        self.message = message,
        self.file = file


db.create_all()
