from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash

app.config['SECRET_KEY'] = 'super-secret'


class Mails(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    mails = db.Column(db.Text())
    group_id = db.Column(db.Integer())

    def __init__(self, name, mails, group_id):
        self.name = name
        self.mails = mails
        self.group_id = group_id


class Groups(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())

    def __init__(self, name):
        self.name = name



class TemplateMessage(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500))
    message = db.Column(db.Text())
    file = db.Column(db.String(500))

    def __init__(self, name, message, file):
        self.name = name,
        self.message = message,
        self.file = file


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    host = db.Column(db.String(100))
    port = db.Column(db.String(100))
    password = db.Column(db.String(100))
    cpassword = db.Column(db.String(100))


    def __init__(self, email, host, port, password, cpassword):
        self.email = email
        self.host = host
        self.port = port
        self.cpassword = cpassword
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

db.create_all()
