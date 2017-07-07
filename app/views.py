import builtins
import socket

from flask import json, flash, session
import smtplib
import random, json
import pyexcel.ext.xls
from flask_paginate import Pagination, get_page_parameter
import os
from os.path import basename

from flask import render_template, request, redirect, url_for

from app import app
from app.models import Mails, db, TemplateMessage, User
from sqlalchemy import update

from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from validate_email import validate_email

app.secret_key = '_\x1ea\xc2>DK\x13\xd0O\xbe1\x13\x1b\x93h2*\x9a+!?\xcb\x8f'


@app.route('/', methods=["POST", "GET"])
def index():
    id = request.args.get('id')
    if id is None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(id)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    template = TemplateMessage.query.all()
    data_len = Mails.query.all()
    data = Mails.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                            per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("index.html", page=page, template=template, per_page=ITEMS_PER_PAGE, data=data,
                           pagination=pagination)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            if loginSite is None:
                flash("Неправильно введен логин")
                return redirect(url_for('login'))
            else:
                if loginSite.check_password(password):
                    session['email'] = loginSite.email
                    session['port'] = loginSite.port
                    session['host'] = loginSite.host
                    session['id'] = loginSite.id
                    return redirect('/')
                else:
                    flash("Неправильно введен пароль")
                    return redirect(url_for('login'))
        else:
            flash("Неправильно введена почта")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        host = request.form['host']
        port = request.form['port']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        loginSite = User.query.filter_by(email=email).first()
        if loginSite:
            flash("Логин занят")
            return redirect(url_for('register'))
        else:
            if (password == cpassword):
                user = User(email=email, host=host, port=port, password=password, cpassword=cpassword)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for("login"))
            else:
                flash("Пароли не совпадают!")
                return redirect(url_for('register'))

    return render_template('registration.html')


@app.route("/profile", methods=['POST', 'GET'])
def profile():
    data = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        host = request.form['host']
        port = request.form['port']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        if (password == cpassword):
            message = update(User).where(User.email == session['email']).values(email=email, host=host, port=port, cpassword=cpassword)
            db.session.execute(message)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("Пароли не совпадают!")
            return redirect(url_for('profile'))
    return render_template('profile.html', data=data)


@app.route('/logout')
def logout():
    # удалить из сессии имя пользователя, если оно там есть
    session.pop('email', None)
    return redirect('/')


@app.route("/dowload", methods=["POST", "GET"])
def dowload():
    if request.method == "POST":
        columnNameOrg = request.form['column1']
        columnEmail = request.form['column2']
        file = request.files['inputFile'].read()
        if not file:
            return "No file"
        sheet = pyexcel.get_sheet(file_type="xlsx", file_content=file)
        for column in sheet.row:
            if validate_email(column[int(columnEmail)-1]):
                addMail = Mails(name=column[int(columnNameOrg)-1], mails=column[int(columnEmail)-1])
                db.session.add(addMail)
                db.session.commit()
        return render_template("dowloads.html", message='Успешно загружено')
    return render_template("dowloads.html")


@app.route("/send", methods=["POST", "GET"])
def send():
    if request.method == "POST":
        list_id = request.form.get('list_id', "").split(",")
        message_id = request.form.get('template')
        message = TemplateMessage.query.filter_by(id=message_id).first()
        for i in list_id:
            data = Mails.query.filter_by(id=i).first()
            sendMessage(data.mails, message.name, message.message, message.file)
    return redirect(url_for('index'))


@app.route("/delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        list_id = request.form.get('list_id_del', "").split(",")
        for id_org in list_id:
            ses1 = Mails.query.filter_by(id=id_org).all()
            for s in ses1:
                db.session.delete(s)
                db.session.commit()
    return redirect(url_for('index'))


@app.route("/template", methods=["GET"])
def template():
    id = request.args.get('id')
    if id == None:
        ITEMS_PER_PAGE = 10
    else:
        ITEMS_PER_PAGE = int(id)
    data_len = TemplateMessage.query.all()
    page = request.args.get(get_page_parameter(), type=int, default=1)
    data = TemplateMessage.query.paginate(page, ITEMS_PER_PAGE, error_out=False).items
    pagination = Pagination(page=page, total=len(data_len), format_total=len(data), format_number=True,
                            per_page=ITEMS_PER_PAGE,
                            css_framework='bootstrap3', active_url='users-page-url', record_name='data')

    return render_template("template.html", page=page, per_page=ITEMS_PER_PAGE, data=data, pagination=pagination)


@app.route("/template/create", methods=["POST", "GET"])
def templateCreate():
    if request.method == 'POST':
        name = request.form.get('name')
        mess = request.form.get('message')
        file = request.files['inputFile']
        if file.filename == '':
            filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = TemplateMessage(name=name, message=mess, file=filename)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('template'))
    return render_template('templateCreate.html')


@app.route("/template/update/", methods=["POST", "GET"])
def templateUpdate():
    id = request.args.get('id')
    if id is None:
        return '', 404
    data = TemplateMessage.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form.get('name')
        mess = request.form.get('message')
        file = request.files['inputFile']
        if file.filename == '':
            if (data.file != ''):
                filename = data.file
            else:
                filename = ''
        else:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        message = update(TemplateMessage).where(TemplateMessage.id == id).values(name=name, message=mess, file=filename)
        db.session.execute(message)
        db.session.commit()
        return redirect(url_for('template'))
    return render_template('templateUpdate.html', data=data)


@app.route("/template/delete/", methods=["POST", "GET"])
def templateDelete():
    id = request.args.get('id')
    if id is None:
        return '', 404
    a = TemplateMessage.query.filter_by(id=id).first()
    if a.file != '':
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], a.file))
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for('template'))


def sendMessage(email, subject, message, files):
    if 'email' in session:
        loginSite = User.query.filter_by(email=session['email']).first()
        if not loginSite:
            flash('Вход не выполнен')
            return url_for('index')
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = loginSite.email
        msg['To'] = email

        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        if files != '':
            path = os.path.join(app.config['UPLOAD_FOLDER'], files)
            with open(path, 'rb') as fp:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(fp.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=files)
            msg.attach(part)
        try:
            s = smtplib.SMTP(host=loginSite.host, port=loginSite.port)  # mail.nic.ru
        except smtplib.SMTPServerDisconnected:
            flash('Сервер недоступен')
            return url_for('index')
        except builtins.TimeoutError:
            flash('Не правильно введен порт')
            return url_for('index')
        except socket.gaierror:
            flash('Не правильно введен хост')
            return url_for('index')
        s.ehlo()
        s.starttls()
        s.ehlo()
        try:
            s.login(loginSite.email, loginSite.cpassword)
        except smtplib.SMTPAuthenticationError:
            flash("Не правильно введена почта или пароль.")
            return url_for('index')
        print(email)
        s.sendmail(loginSite.email, email, msg.as_string())
        s.quit()
    else:
        flash('Вход не выполнен')
        return url_for('index')
